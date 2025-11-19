#!/bin/bash
#
# Cutie-Pi Dashboard Uninstaller
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

INSTALL_DIR="/opt/cutie-pi"
CONFIG_DIR="/etc/cutie-pi"
SERVICE_FILE="/etc/systemd/system/cutie-pi.service"

echo "Cutie-Pi Uninstaller"
echo "===================="
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Error: This script must be run as root${NC}"
   echo "Please run: sudo bash uninstall.sh"
   exit 1
fi

# Confirm uninstallation
read -p "Are you sure you want to uninstall Cutie-Pi? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstallation cancelled."
    exit 0
fi

echo -e "${YELLOW}[1/4]${NC} Stopping service..."
systemctl stop cutie-pi.service 2>/dev/null || true
systemctl disable cutie-pi.service 2>/dev/null || true

echo -e "${YELLOW}[2/4]${NC} Removing service file..."
rm -f "$SERVICE_FILE"
systemctl daemon-reload

echo -e "${YELLOW}[3/4]${NC} Removing application files..."
rm -rf "$INSTALL_DIR"

echo -e "${YELLOW}[4/4]${NC} Removing configuration..."
read -p "Remove configuration files? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$CONFIG_DIR"
    echo "Configuration removed."
else
    echo -e "Configuration kept at: ${YELLOW}$CONFIG_DIR${NC}"
fi

echo ""
echo -e "${GREEN}Cutie-Pi has been uninstalled.${NC}"
echo ""
echo "Note: System dependencies (python3-pygame, xserver-xorg) were not removed."
echo "To remove them: sudo apt remove python3-pygame xserver-xorg"
echo ""
