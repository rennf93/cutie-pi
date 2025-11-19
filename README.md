# Cutie-Pi

A pixel-art dashboard for Pi-hole on small LCD screens. Inspired by Flipper Zero's retro aesthetic.

## Features

- 5 swipeable screens: Stats, Graph, Top Blocked, Clients, System Info
- Pixel-art 8-bit style with Press Start 2P font
- Touch and keyboard navigation
- Real-time system monitoring (CPU, RAM, Temp, Fan, Disk)
- Scanline CRT effect

## Requirements

- Raspberry Pi with LCD screen (tested on 3.5" 480x320)
- Pi-hole v6
- Python 3.9+

## Installation

```bash
git clone https://github.com/yourusername/cutie-pi.git
cd cutie-pi
sudo bash install.sh --pihole-password "YOUR_PIHOLE_PASSWORD"
```

### Installation Options

```bash
sudo bash install.sh [OPTIONS]

Options:
  --pihole-password PASSWORD   Pi-hole API password
  --pihole-api URL             Pi-hole API URL (default: http://localhost/api)
  --screen-width WIDTH         Screen width in pixels (default: 480)
  --screen-height HEIGHT       Screen height in pixels (default: 320)
```

## Configuration

Configuration is stored in `/etc/cutie-pi/config`:

```bash
# Pi-hole API settings
CUTIE_PIHOLE_API="http://localhost/api"
CUTIE_PIHOLE_PASSWORD="your_password"

# Display settings
CUTIE_SCREEN_WIDTH="480"
CUTIE_SCREEN_HEIGHT="320"
CUTIE_FPS="30"

# Update intervals (seconds)
CUTIE_API_INTERVAL="5"
CUTIE_SYSTEM_INTERVAL="2"
```

## Usage

```bash
# Start
sudo systemctl start cutie-pi

# Stop
sudo systemctl stop cutie-pi

# View logs
sudo journalctl -u cutie-pi -f

# Check status
sudo systemctl status cutie-pi
```

## Controls

- **Swipe left/right**: Change screens
- **Arrow keys**: Change screens
- **ESC**: Exit

## Uninstall

```bash
sudo bash uninstall.sh
```

## Structure

```
cutie-pi/
├── main.py              # Entry point
├── config.py            # Configuration from env vars
├── api/
│   └── pihole.py        # Pi-hole API client
├── screens/
│   ├── base.py          # Base screen class
│   ├── stats.py         # Pi-hole stats
│   ├── graph.py         # Query graph
│   ├── blocked.py       # Top blocked domains
│   ├── clients.py       # Top clients
│   └── system.py        # System info
├── ui/
│   ├── colors.py        # Color definitions
│   ├── fonts.py         # Pixel font
│   └── components.py    # UI components
└── utils/
    └── system_info.py   # System info gathering
```

## License

MIT
