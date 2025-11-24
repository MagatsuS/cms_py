# Raspberry Pi Setup Guide - Browser-Based Player

This guide shows you how to set up the CMS digital signage player on Raspberry Pi using the browser-based approach.

## What This Does

Opens your cms_dupe player URL (`http://your-server:8000/player/PLAYER-XXXXXX`) in fullscreen kiosk mode on Raspberry Pi.

## Prerequisites

- Raspberry Pi 3B+ or 4 (recommended)
- Raspberry Pi OS (Bullseye or newer)
- Network connection to cms_dupe server
- Player created in cms_dupe web interface

## Quick Setup

### 1. Prepare Raspberry Pi

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y chromium-browser unclutter python3 python3-pip python3-venv

# Install X server utilities (if not using desktop)
sudo apt install -y xserver-xorg x11-xserver-utils xinit
```

### 2. Install cms_py

```bash
# Create directory
cd ~
mkdir cms_player
cd cms_player

# Copy cms_py files to Raspberry Pi
# (Use USB drive, SCP, or git clone)

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install python-dotenv
```

### 3. Configure Player

```bash
# Create .env file
cp .env.example .env

# Edit configuration
nano .env
```

Set these values:
```env
CMS_URL=http://YOUR_SERVER_IP:8000
PLAYER_CODE=PLAYER-XXXXXXXX
PLAYER_URL=http://YOUR_SERVER_IP:8000/player/PLAYER-XXXXXXXX
```

Replace:
- `YOUR_SERVER_IP` with your cms_dupe server IP (e.g., `192.168.1.100`)
- `PLAYER-XXXXXXXX` with your actual player code

### 4. Test Player

```bash
# Run player
python player_browser.py
```

This should open the player in fullscreen. Press F11 to exit fullscreen.

## Auto-Start on Boot

### Method 1: Systemd Service (Recommended)

Create service file:
```bash
sudo nano /etc/systemd/system/cms-player.service
```

Add:
```ini
[Unit]
Description=CMS Digital Signage Player (Browser)
After=network.target graphical.target

[Service]
Type=simple
User=pi
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/pi/.Xauthority
WorkingDirectory=/home/pi/cms_player
ExecStartPre=/bin/sleep 10
ExecStart=/home/pi/cms_player/venv/bin/python /home/pi/cms_player/player_browser.py
Restart=always
RestartSec=10

[Install]
WantedBy=graphical.target
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

### Method 2: Autostart (Desktop Mode)

Create autostart file:
```bash
mkdir -p ~/.config/autostart
nano ~/.config/autostart/cms-player.desktop
```

Add:
```ini
[Desktop Entry]
Type=Application
Name=CMS Player
Exec=/home/pi/cms_player/venv/bin/python /home/pi/cms_player/player_browser.py
Terminal=false
```

### Method 3: Simple Chromium Kiosk (No Python)

Edit autostart:
```bash
nano ~/.config/lxsession/LXDE-pi/autostart
```

Add:
```bash
@xset s off
@xset -dpms
@xset s noblank
@chromium-browser --kiosk --noerrdialogs --disable-infobars http://YOUR_SERVER_IP:8000/player/PLAYER-XXXXXXXX
```

## Hide Mouse Cursor

```bash
# Install unclutter
sudo apt install unclutter -y

# Add to autostart
echo "@unclutter -idle 0.1 -root" >> ~/.config/lxsession/LXDE-pi/autostart
```

## Disable Screen Blanking

```bash
# Edit config
sudo nano /etc/lightdm/lightdm.conf
```

Find `[Seat:*]` section and add:
```ini
xserver-command=X -s 0 -dpms
```

## Network Configuration

### Connect to WiFi

```bash
sudo raspi-config
```

Select: `System Options` → `Wireless LAN`

### Static IP (Optional)

```bash
sudo nano /etc/dhcpcd.conf
```

Add:
```
interface wlan0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8
```

## Troubleshooting

### Player doesn't start

```bash
# Check service status
sudo systemctl status cms-player

# View logs
sudo journalctl -u cms-player -f

# Test manually
cd ~/cms_player
source venv/bin/activate
python player_browser.py
```

### Black screen

- Check `DISPLAY` environment variable: `echo $DISPLAY` (should be `:0`)
- Check X server is running: `ps aux | grep X`
- Try running as user `pi`, not `root`

### Cannot connect to server

- Check network: `ping YOUR_SERVER_IP`
- Check server is running
- Check firewall allows port 8000
- Try accessing in browser manually first

### Screen blanks/sleeps

```bash
# Disable screen blanking
xset s off
xset -dpms
xset s noblank
```

### Chromium crashes

```bash
# Clear browser cache
rm -rf ~/.cache/chromium
rm -rf ~/.config/chromium

# Restart player
sudo systemctl restart cms-player
```

## Performance Tips

1. **Reduce Memory Usage**:
   ```bash
   # Limit Chromium cache
   chromium-browser --disk-cache-size=1
   ```

2. **Overclock Raspberry Pi** (at your own risk):
   ```bash
   sudo nano /boot/config.txt
   ```
   Add:
   ```
   over_voltage=2
   arm_freq=1750
   ```

3. **Use Lite OS**: Install Raspberry Pi OS Lite (no desktop) and run X server only for browser

## Monitoring

### Check if player is running

```bash
ps aux | grep chromium
```

### Check CPU/Memory usage

```bash
htop
```

### Auto-restart if crashed

The systemd service includes `Restart=always` which will restart if it crashes.

## Updating

```bash
cd ~/cms_player
git pull  # If using git
# Or re-copy files

sudo systemctl restart cms-player
```

## Remote Management

### SSH Access

```bash
# Enable SSH
sudo raspi-config
```

Select: `Interface Options` → `SSH` → `Enable`

Connect from another computer:
```bash
ssh pi@192.168.1.100
```

### VNC Access (Optional)

```bash
sudo apt install realvnc-vnc-server -y
sudo raspi-config
```

Select: `Interface Options` → `VNC` → `Enable`

## Complete Auto-Start Script

Create startup script:
```bash
nano ~/cms_player/start_player.sh
```

Add:
```bash
#!/bin/bash

# Disable screen blanking
xset s off
xset -dpms
xset s noblank

# Hide cursor
unclutter -idle 0.1 -root &

# Start player
cd ~/cms_player
source venv/bin/activate
python player_browser.py
```

Make executable:
```bash
chmod +x ~/cms_player/start_player.sh
```

## Tips

- **Multiple Players**: Use different player codes for each Raspberry Pi
- **Content Updates**: Content updates automatically when you refresh/redeploy in cms_dupe
- **Scheduled Reboot**: Add cron job to reboot daily at 3am: `0 3 * * * sudo reboot`

## Support

If you encounter issues:
1. Check service logs: `sudo journalctl -u cms-player -f`
2. Test browser manually: Open chromium and visit player URL
3. Check network connectivity
4. Verify player exists in cms_dupe

---

**Last Updated**: 2025-11-24
