# CMS_PY - Raspberry Pi Digital Signage Player

Python-based player application for Raspberry Pi that connects to **cms_dupe** backend and displays digital signage content on TV screens.

## What is this?

This is **NOT** a full CMS system. This is only the **player application** that runs on Raspberry Pi devices.

- **Backend (CMS)**: cms_dupe (Laravel) - manages content, playlists, users
- **Player (This)**: cms_py (Python) - displays content on TV screens

**One Raspberry Pi = One Player = One TV Screen**

## Quick Start

### Prerequisites

- **Python 3.10+** installed
- **cms_dupe** backend running (Laravel CMS)
- **Player code** from cms_dupe (format: `PLR-XXXXXXXX`)

### Installation

```bash
# 1. Clone or download this project
cd cms_py

# 2. Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env
# Edit .env and set your CMS_API_URL and PLAYER_CODE

# 5. Run the player
python main.py
```

## Configuration

### Get Your Player Code

1. Go to cms_dupe web interface
2. Navigate to **Players** section
3. Click **Add Player** or **Register Player**
4. Copy the player code (e.g., `PLR-AB12CD34`)

### Configure .env File

```bash
# CMS API Configuration
CMS_API_URL=http://localhost/cms_dupe/public/api/v1
# or use your domain: http://cms-dupe.test/api/v1

# Player Configuration
PLAYER_CODE=PLR-AB12CD34  # <-- Your player code from cms_dupe
PLAYER_NAME=Office TV
PLAYER_LOCATION=Main Office

# Display Settings
SCREEN_RESOLUTION=1920x1080
FULLSCREEN=True

# Cache Settings
CACHE_DIR=storage/cache
MAX_CACHE_SIZE_MB=2000

# Heartbeat (how often to contact server)
HEARTBEAT_INTERVAL=30

# Logging
DEBUG=False
LOG_LEVEL=INFO
```

## Usage

### Running the Player

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run the player
python main.py
```

### First Time Setup

If you haven't configured `.env` yet, the application will prompt you:

```
===================================================
  CMS_PY - Digital Signage Player
===================================================

Player code not configured in .env file.

Please enter your player code from cms_dupe:
(Format: PLR-XXXXXXXX)

Player Code: PLR-AB12CD34

Save this player code to .env file? (y/n): y
```

### Expected Output

```
2025-11-24 10:00:00 - INFO - Starting CMS_PY Digital Signage Player
2025-11-24 10:00:00 - INFO - Connecting to CMS API: http://localhost/cms_dupe/public/api/v1
2025-11-24 10:00:00 - INFO - Player Code: PLR-AB12CD34
2025-11-24 10:00:00 - INFO - Authenticating with CMS...
2025-11-24 10:00:01 - INFO - Successfully authenticated! Player: Office TV
2025-11-24 10:00:01 - INFO - Location: Main Office
2025-11-24 10:00:01 - INFO - Starting player...
2025-11-24 10:00:01 - INFO - Loading playlist from server...
2025-11-24 10:00:02 - INFO - Loaded playlist: Morning Announcements
2025-11-24 10:00:02 - INFO - Total assets: 5
2025-11-24 10:00:02 - INFO - Caching 5 assets...
2025-11-24 10:00:05 - INFO - Successfully cached 5 assets
2025-11-24 10:00:05 - INFO - Starting playback loop...
2025-11-24 10:00:05 - INFO - Playing: Welcome Banner (image) - Duration: 10s
```

## How It Works

### 1. Authentication
```
┌────────────┐  Player Code   ┌──────────┐
│  cms_py    │───────────────►│ cms_dupe │
│  (Player)  │◄───────────────│ (Backend)│
└────────────┘  API Token     └──────────┘
```

### 2. Fetch Playlist
```
┌────────────┐  GET /playlist ┌──────────┐
│  cms_py    │───────────────►│ cms_dupe │
│            │◄───────────────│          │
└────────────┘  Assets List   └──────────┘
```

### 3. Download Content
```
┌────────────┐  Download      ┌──────────────┐
│  cms_py    │───────────────►│ DigitalOcean │
│            │                │ Spaces (CDN) │
└────────────┘                └──────────────┘
     ▼
 [Local Cache]
```

### 4. Display & Report
```
┌────────────┐  Heartbeat     ┌──────────┐
│  cms_py    │───────────────►│ cms_dupe │
│            │  Playback Log  │          │
│            │───────────────►│          │
└────────────┘                └──────────┘
```

## Project Structure

```
cms_py/
├── app/
│   ├── api_client.py       # API communication with cms_dupe
│   ├── cache_manager.py    # Download and cache media files
│   └── player.py           # Main playback logic
├── storage/
│   ├── cache/              # Downloaded media files
│   └── logs/               # Application logs
├── .env                    # Your configuration
├── main.py                 # Entry point - run this
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Features

### ✅ Implemented
- Player authentication with unique code (`PLR-XXXXXXXX`)
- API communication with cms_dupe
- Download and cache media files
- Playlist management
- Heartbeat reporting (every 30 seconds)
- Playback status logging
- Automatic playlist synchronization
- Offline content caching

### 🚧 Coming Soon
- Actual fullscreen video/image display (currently placeholder)
- VLC video playback
- Image slideshow
- HTML content rendering
- HDMI-CEC TV control
- Auto-start on Raspberry Pi boot

## Testing Without Raspberry Pi

You can test on Windows/Mac/Linux:

1. Install Python 3.10+
2. Follow installation steps above
3. Run `python main.py`
4. Check logs in `storage/logs/player.log`

The player will download content and simulate playback (without actual display).

## Raspberry Pi Setup

### Install Raspberry Pi OS

1. Download Raspberry Pi Imager: https://www.raspberrypi.com/software/
2. Flash Raspberry Pi OS to MicroSD card
3. Boot Raspberry Pi

### Install Python & Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install VLC (for video playback)
sudo apt install vlc -y

# Install system dependencies
sudo apt install libvlc-dev -y
```

### Install CMS_PY

```bash
# Clone or copy cms_py to Raspberry Pi
cd ~
# (copy cms_py folder here)

cd cms_py

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Edit and set PLAYER_CODE and CMS_API_URL
```

### Auto-Start on Boot

Create systemd service:

```bash
sudo nano /etc/systemd/system/cms-player.service
```

Add:

```ini
[Unit]
Description=CMS Digital Signage Player
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/cms_py
Environment="PATH=/home/pi/cms_py/venv/bin"
ExecStart=/home/pi/cms_py/venv/bin/python /home/pi/cms_py/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable cms-player
sudo systemctl start cms-player

# Check status
sudo systemctl status cms-player

# View logs
sudo journalctl -u cms-player -f
```

## Troubleshooting

### Cannot connect to CMS

**Problem**: `Authentication failed!`

**Solution**:
- Check `CMS_API_URL` in `.env` is correct
- Make sure cms_dupe is running
- Verify player code exists in cms_dupe database

### Player code invalid

**Problem**: `Player not found`

**Solution**:
- Create player in cms_dupe web interface first
- Copy the exact player code (e.g., `PLR-AB12CD34`)
- Player codes are case-sensitive

### No playlist assigned

**Problem**: `No playlist assigned to this player`

**Solution**:
- Go to cms_dupe web interface
- Assign a playlist to your player
- Or deploy content to your player

### Port errors on Windows

**Problem**: `Address already in use`

**Solution**:
- This is a player application, it doesn't need to open ports
- If you see this error, another application is using the network

## API Endpoints Used

The player communicates with cms_dupe using these endpoints:

| Endpoint | Purpose |
|----------|---------|
| `POST /api/v1/player/authenticate` | Get API token |
| `POST /api/v1/player/heartbeat` | Send status every 30s |
| `GET /api/v1/player/playlist` | Get assigned playlist |
| `GET /api/v1/player/deployments/pending` | Check for updates |
| `POST /api/v1/player/playback/report` | Log what's playing |

## Development

### Testing Changes

```bash
# Edit code
# ...

# Restart player
python main.py
```

### View Logs

```bash
# Real-time logs
tail -f storage/logs/player.log

# Or check console output
```

### Clear Cache

```bash
# Remove cached files
rm -rf storage/cache/*

# Player will re-download content
```

## Support

For issues:
1. Check `storage/logs/player.log`
2. Verify cms_dupe is running
3. Test API URL in browser: `http://your-url/api/v1/player/info`

## Related Projects

- **cms_dupe**: Laravel-based CMS backend (`C:\laragon\www\cms_dupe`)

## License

(To be determined)

---

**Project Type**: Raspberry Pi Player Application
**Backend Required**: cms_dupe (Laravel)
**Hardware**: Raspberry Pi 3B+ or 4
**Last Updated**: 2025-11-24
