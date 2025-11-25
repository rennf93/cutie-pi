#!/bin/bash
#
# Cutie-Pi Dashboard Installer
# A pixel-art Pi-hole dashboard for small LCD screens
#
# One-liner install:
#   curl -sSL https://raw.githubusercontent.com/rennf93/cutie-pi/v1.0.1/install.sh | sudo bash
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# GitHub repo info
GITHUB_REPO="rennf93/cutie-pi"
GITHUB_BRANCH="v1.0.1"  # Use tagged release, not master

# Default values
INSTALL_DIR="/opt/cutie-pi"
CONFIG_FILE="/etc/cutie-pi/config"
SERVICE_FILE="/etc/systemd/system/cutie-pi.service"
TMP_DIR="/tmp/cutie-pi-install"

# Configuration defaults
DEFAULT_PIHOLE_API="http://localhost/api"
DEFAULT_PIHOLE_PASSWORD=""
DEFAULT_SCREEN_WIDTH="480"
DEFAULT_SCREEN_HEIGHT="320"
DEFAULT_THEME="default"

# Version from source
VERSION="1.0.1"

print_banner() {
    echo -e "${CYAN}"
    echo "  ██████╗██╗   ██╗████████╗██╗███████╗      ██████╗ ██╗"
    echo " ██╔════╝██║   ██║╚══██╔══╝██║██╔════╝      ██╔══██╗██║"
    echo " ██║     ██║   ██║   ██║   ██║█████╗  █████╗██████╔╝██║"
    echo " ██║     ██║   ██║   ██║   ██║██╔══╝  ╚════╝██╔═══╝ ██║"
    echo " ╚██████╗╚██████╔╝   ██║   ██║███████╗      ██║     ██║"
    echo "  ╚═════╝ ╚═════╝    ╚═╝   ╚═╝╚══════╝      ╚═╝     ╚═╝"
    echo -e "${NC}"
    echo "Pixel-art Pi-hole Dashboard v${VERSION}"
    echo "============================================"
    echo ""
}

print_usage() {
    echo "Usage: sudo bash install.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --pihole-password PASSWORD   Pi-hole API password"
    echo "  --pihole-api URL             Pi-hole API URL (default: http://localhost/api)"
    echo "  --screen-width WIDTH         Screen width in pixels (default: 480)"
    echo "  --screen-height HEIGHT       Screen height in pixels (default: 320)"
    echo "  --theme THEME                Color theme (default: default)"
    echo "  --update                     Update existing installation"
    echo "  --version                    Show version and exit"
    echo "  --help                       Show this help message"
    echo ""
    echo "One-liner install from GitHub:"
    echo "  curl -sSL https://raw.githubusercontent.com/${GITHUB_REPO}/${GITHUB_BRANCH}/install.sh | sudo bash"
    echo ""
    echo "Available themes:"
    echo "  default    - Classic Pi-hole green"
    echo "  monochrome - Black and white"
    echo "  neon       - Vibrant neon colors"
    echo "  ocean      - Cool blue tones"
    echo "  sunset     - Warm orange/red tones"
    echo ""
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}Error: This script must be run as root${NC}"
        echo "Please run: sudo bash install.sh"
        exit 1
    fi
}

get_actual_user() {
    ACTUAL_USER="${SUDO_USER:-$USER}"
    ACTUAL_HOME=$(getent passwd "$ACTUAL_USER" | cut -d: -f6)
    FONT_DIR="$ACTUAL_HOME/.fonts"
}

install_dependencies() {
    echo -e "${GREEN}[1/6]${NC} Installing system dependencies..."
    apt-get update -qq
    apt-get install -y -qq python3 python3-pygame python3-requests xserver-xorg xinit fonts-dejavu curl > /dev/null

    echo -e "${GREEN}[2/6]${NC} Verifying Python dependencies..."
    python3 -c "import pygame, requests" 2>/dev/null || {
        echo -e "${RED}Error: Python dependencies not installed correctly${NC}"
        exit 1
    }
}

install_font() {
    echo -e "${GREEN}[3/6]${NC} Installing pixel font..."
    mkdir -p "$FONT_DIR"
    if [[ ! -f "$FONT_DIR/PressStart2P.ttf" ]]; then
        echo "Downloading Press Start 2P font..."
        curl -sL "https://github.com/google/fonts/raw/main/ofl/pressstart2p/PressStart2P-Regular.ttf" \
            -o "$FONT_DIR/PressStart2P.ttf"
        chown "$ACTUAL_USER:$ACTUAL_USER" "$FONT_DIR/PressStart2P.ttf"
    fi
}

install_application() {
    echo -e "${GREEN}[4/6]${NC} Installing cutie-pi..."

    # Create installation directory
    mkdir -p "$INSTALL_DIR"

    # Check if we're running from local source or need to download
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)" || SCRIPT_DIR=""

    if [[ -n "$SCRIPT_DIR" && -f "$SCRIPT_DIR/main.py" ]]; then
        # Local install - copy from source directory
        echo "Installing from local source..."

        # Copy Python files
        for file in "$SCRIPT_DIR"/*.py; do
            [[ -f "$file" ]] && cp "$file" "$INSTALL_DIR/"
        done

        # Copy directories
        for dir in api screens ui utils; do
            if [[ -d "$SCRIPT_DIR/$dir" ]]; then
                rm -rf "$INSTALL_DIR/$dir"
                cp -r "$SCRIPT_DIR/$dir" "$INSTALL_DIR/"
            fi
        done
    else
        # Remote install - download from GitHub
        echo "Downloading from GitHub..."

        # Clean up any previous download
        rm -rf "$TMP_DIR"
        mkdir -p "$TMP_DIR"

        # Download the repository
        curl -sL "https://github.com/${GITHUB_REPO}/archive/${GITHUB_BRANCH}.tar.gz" | tar -xz -C "$TMP_DIR" --strip-components=1

        # Copy files to install directory
        cp "$TMP_DIR"/*.py "$INSTALL_DIR/"
        for dir in api screens ui utils; do
            rm -rf "$INSTALL_DIR/$dir"
            cp -r "$TMP_DIR/$dir" "$INSTALL_DIR/"
        done

        # Clean up
        rm -rf "$TMP_DIR"
    fi

    # Set permissions
    chmod -R 755 "$INSTALL_DIR"

    # Write version file
    echo "$VERSION" > "$INSTALL_DIR/.version"
}

create_config() {
    echo -e "${GREEN}[5/6]${NC} Creating configuration..."

    # Create config directory
    mkdir -p /etc/cutie-pi

    # Check if config already exists (for updates)
    if [[ -f "$CONFIG_FILE" && "$UPDATE_MODE" == "true" ]]; then
        echo "Preserving existing configuration..."
        return
    fi

    # Write configuration file
    cat > "$CONFIG_FILE" << EOF
# Cutie-Pi Configuration
# Generated by installer v${VERSION} on $(date)

# Pi-hole API settings
CUTIE_PIHOLE_API="$PIHOLE_API"
CUTIE_PIHOLE_PASSWORD="$PIHOLE_PASSWORD"

# Display settings
CUTIE_SCREEN_WIDTH="$SCREEN_WIDTH"
CUTIE_SCREEN_HEIGHT="$SCREEN_HEIGHT"
CUTIE_FPS="30"

# Theme settings
CUTIE_THEME="$THEME"

# Update intervals (seconds)
CUTIE_API_INTERVAL="5"
CUTIE_SYSTEM_INTERVAL="2"

# Swipe detection threshold
CUTIE_SWIPE_THRESHOLD="50"
EOF

    chmod 600 "$CONFIG_FILE"
}

setup_service() {
    echo -e "${GREEN}[6/6]${NC} Setting up systemd service..."

    # Configure Xwrapper to allow anybody to run X server
    if [[ -f /etc/X11/Xwrapper.config ]]; then
        sed -i 's/allowed_users=console/allowed_users=anybody/' /etc/X11/Xwrapper.config
    else
        mkdir -p /etc/X11
        echo "allowed_users=anybody" > /etc/X11/Xwrapper.config
    fi

    # Create systemd service
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Cutie-Pi Dashboard v${VERSION}
After=network.target pihole-FTL.service
Wants=pihole-FTL.service

[Service]
Type=simple
User=$ACTUAL_USER
EnvironmentFile=$CONFIG_FILE
ExecStart=/usr/bin/xinit /usr/bin/python3 $INSTALL_DIR/main.py -- :0 -nocursor
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable cutie-pi.service
}

print_success() {
    echo ""
    echo -e "${GREEN}============================================${NC}"
    if [[ "$UPDATE_MODE" == "true" ]]; then
        echo -e "${GREEN}Update complete! (v${VERSION})${NC}"
    else
        echo -e "${GREEN}Installation complete! (v${VERSION})${NC}"
    fi
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo "Configuration file: $CONFIG_FILE"
    echo "Installation directory: $INSTALL_DIR"
    echo ""
    echo "Commands:"
    echo "  Start dashboard:   sudo systemctl start cutie-pi"
    echo "  Stop dashboard:    sudo systemctl stop cutie-pi"
    echo "  Restart dashboard: sudo systemctl restart cutie-pi"
    echo "  View logs:         sudo journalctl -u cutie-pi -f"
    echo "  Edit config:       sudo nano $CONFIG_FILE"
    echo "  Update:            sudo bash install.sh --update"
    echo "  Uninstall:         sudo bash uninstall.sh"
    echo ""
    if [[ -z "$PIHOLE_PASSWORD" ]]; then
        echo -e "${YELLOW}Note: You may need to configure your Pi-hole password in:${NC}"
        echo -e "${YELLOW}      $CONFIG_FILE${NC}"
        echo ""
    fi
    echo "Start now with: sudo systemctl start cutie-pi"
    echo ""
}

# Main script starts here
print_banner

# Parse command line arguments
UPDATE_MODE="false"
while [[ $# -gt 0 ]]; do
    case $1 in
        --pihole-password)
            PIHOLE_PASSWORD="$2"
            shift 2
            ;;
        --pihole-api)
            PIHOLE_API="$2"
            shift 2
            ;;
        --screen-width)
            SCREEN_WIDTH="$2"
            shift 2
            ;;
        --screen-height)
            SCREEN_HEIGHT="$2"
            shift 2
            ;;
        --theme)
            THEME="$2"
            shift 2
            ;;
        --update)
            UPDATE_MODE="true"
            shift
            ;;
        --version)
            echo "Cutie-Pi v${VERSION}"
            exit 0
            ;;
        --help)
            print_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            print_usage
            exit 1
            ;;
    esac
done

# Set defaults if not provided
PIHOLE_API="${PIHOLE_API:-$DEFAULT_PIHOLE_API}"
PIHOLE_PASSWORD="${PIHOLE_PASSWORD:-$DEFAULT_PIHOLE_PASSWORD}"
SCREEN_WIDTH="${SCREEN_WIDTH:-$DEFAULT_SCREEN_WIDTH}"
SCREEN_HEIGHT="${SCREEN_HEIGHT:-$DEFAULT_SCREEN_HEIGHT}"
THEME="${THEME:-$DEFAULT_THEME}"

# Run installation
check_root
get_actual_user
install_dependencies
install_font
install_application
create_config
setup_service
print_success
