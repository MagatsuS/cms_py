# CMS_PY - Raspberry Pi Digital Signage Player

## Project Overview

CMS_PY is a **Python-based player application** designed to run on **Raspberry Pi** devices. It connects to the **cms_dupe** backend (Laravel CMS) and displays digital signage content on TV screens.

**Important:** This is NOT a full CMS backend. It's only the player application that runs on Raspberry Pi hardware.

## Purpose

This application enables a Raspberry Pi to:
- Authenticate with cms_dupe using a unique player code (format: `PLR-XXXXXXXX`)
- Download and cache media content (images, videos, HTML)
- Display content in fullscreen on connected TV screens
- Report playback status back to cms_dupe
- Automatically sync when new content is deployed

## Architecture

```
┌─────────────────┐         API          ┌──────────────────┐
│   cms_dupe      │◄─────────────────────►│  Raspberry Pi    │
│   (Laravel)     │      (HTTP/REST)      │  + cms_py        │
│   Backend       │                       │  (Python Player) │
└─────────────────┘                       └────────┬─────────┘
                                                   │ HDMI
                                                   ▼
                                             ┌──────────┐
                                             │  TV      │
                                             │  Screen  │
                                             └──────────┘
```

## Workflow

### 1. Initial Setup
- Install cms_py on Raspberry Pi
- Configure player code from cms_dupe
- Run application

### 2. Authentication
- Player authenticates with cms_dupe using player code `PLR-XXXXXXXX`
- Receives API token for subsequent requests
- Gets player configuration (name, location, settings)

### 3. Content Synchronization
- Fetches assigned playlist from cms_dupe
- Downloads all media files to local cache
- Stores files for offline playback

### 4. Content Playback
- Displays content in fullscreen loop
- Respects duration settings for each asset
- Handles images, videos, and HTML content
- Seamless transitions between assets

### 5. Status Reporting
- Sends heartbeat every 30 seconds
- Reports current playback status
- Checks for playlist updates
- Logs playback analytics

## Technology Stack

### Core
- **Python 3.10+** - Main programming language
- **requests** - HTTP client for API communication
- **python-dotenv** - Environment configuration

### Media Playback (Planned)
- **python-vlc** - Video playback
- **PyQt5** - GUI framework for fullscreen display
- **Pillow** - Image processing

### System
- **psutil** - System monitoring (CPU, memory, disk)

## Project Structure

```
cms_py/
├── app/
│   ├── __init__.py
│   ├── api_client.py        # CMS API communication
│   ├── cache_manager.py     # Media file caching
│   └── player.py            # Main playback logic
├── storage/
│   ├── cache/               # Cached media files
│   └── logs/                # Application logs
├── .env                     # Configuration (create from .env.example)
├── .env.example             # Configuration template
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
└── README.md                # Setup instructions
```

## Key Features

### Implemented
✅ Player authentication with unique code
✅ API client for cms_dupe communication
✅ Media file caching system
✅ Playlist download and management
✅ Heartbeat reporting
✅ Playback status logging
✅ Automatic playlist synchronization
✅ Deployment checking
✅ Offline caching support

### To Be Implemented
- [ ] Actual fullscreen media display (currently placeholder)
- [ ] VLC video playback integration
- [ ] Image slideshow with transitions
- [ ] HTML content rendering
- [ ] HDMI-CEC TV control
- [ ] System health monitoring
- [ ] Auto-start on boot (systemd service)
- [ ] Web configuration interface
- [ ] OTA updates

## API Integration

CMS_PY connects to cms_dupe's REST API:

### Base URL
```
http://your-cms-dupe-url/api/v1
```

### Key Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/player/authenticate` | POST | Authenticate with player code |
| `/player/heartbeat` | POST | Send status updates |
| `/player/playlist` | GET | Get current playlist and assets |
| `/player/deployments/pending` | GET | Check for new deployments |
| `/player/playback/report` | POST | Report playback activity |
| `/player/info` | GET | Get player configuration |

### Authentication Flow

```python
# 1. Authenticate
POST /api/v1/player/authenticate
{
  "code": "PLR-XXXXXXXX"
}

# Response
{
  "success": true,
  "data": {
    "player": {...},
    "token": "1|xxxxxxxxxxxxx"
  }
}

# 2. Use token for all requests
Headers: {
  "Authorization": "Bearer 1|xxxxxxxxxxxxx"
}
```

## Configuration

### Environment Variables (.env)

```bash
# CMS API Configuration
CMS_API_URL=http://localhost/cms_dupe/public/api/v1
PLAYER_CODE=PLR-XXXXXXXX
PLAYER_NAME=My TV Screen
PLAYER_LOCATION=Office Lobby

# Display Settings
SCREEN_RESOLUTION=1920x1080
FULLSCREEN=True

# Cache Settings
CACHE_DIR=storage/cache
MAX_CACHE_SIZE_MB=2000

# Heartbeat
HEARTBEAT_INTERVAL=30

# Debug
DEBUG=False
LOG_LEVEL=INFO
```

## Setup Requirements

### Hardware
- **Raspberry Pi 4** (recommended) or Pi 3B+
- **8GB+ MicroSD Card** for OS
- **USB Drive or External Storage** (optional, for large cache)
- **HDMI Cable** to connect to TV
- **Internet Connection** (WiFi or Ethernet)

### Software
- **Raspberry Pi OS** (Bullseye or newer)
- **Python 3.10+**
- **VLC Media Player** (for video playback)

## Installation

See **README.md** for detailed setup instructions.

## Use Cases

### Typical Deployment
1. Admin creates player in cms_dupe web interface
2. Gets player code (e.g., `PLR-AB12CD34`)
3. Installs cms_py on Raspberry Pi
4. Enters player code
5. Application authenticates and starts displaying content

### One Raspberry Pi = One Player = One TV
Each Raspberry Pi device:
- Has a unique player code
- Connects to one TV screen via HDMI
- Displays its assigned playlist
- Operates independently from other players

## Development Status

**Status**: Core features implemented, media playback to be finalized

**Current Phase**: Foundation complete, ready for media player integration

**Next Steps**:
1. Implement actual VLC video playback
2. Add PyQt5 fullscreen image display
3. Add HTML rendering with WebView
4. Test on actual Raspberry Pi hardware
5. Implement HDMI-CEC control
6. Create systemd service for auto-start

## Reference Backend

This player connects to **cms_dupe** at:
```
C:\laragon\www\cms_dupe
```

API documentation from cms_dupe should be consulted for any API changes or additions.

## Notes

- **No Raspberry Pi Required for Development**: You can test on Windows/Mac/Linux
- **Offline Support**: Once content is cached, player works without internet
- **Automatic Updates**: When cms_dupe deploys new content, player auto-syncs
- **Lightweight**: Designed to run efficiently on Raspberry Pi hardware

---

**Project Type**: Raspberry Pi Player Application
**Backend**: cms_dupe (Laravel)
**Last Updated**: 2025-11-24
