#!/bin/bash

# Automatic Cartridge Scanning JIG - Auto-start setup script
# This script sets up the jig to automatically start on boot

set -e

# Configuration
PROJECT_DIR="/home/qateam/Desktop/Project file"
SERVICE_NAME="batch-jig.service"
SERVICE_USER="qateam"

echo "Setting up Automatic Cartridge Scanning JIG for auto-start on boot..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script as root (use sudo)"
    exit 1
fi

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Creating project directory: $PROJECT_DIR"
    mkdir -p "$PROJECT_DIR"
    chown $SERVICE_USER:$SERVICE_USER "$PROJECT_DIR"
fi

# Copy project files if they don't exist
if [ ! -f "$PROJECT_DIR/main.py" ]; then
    echo "Please copy your project files to $PROJECT_DIR first!"
    echo "Required files: main.py, config.py, settings.ini, and all other Python modules"
    exit 1
fi

# Install required Python packages
echo "Installing required Python packages..."
apt-get update
apt-get install -y python3 python3-pip python3-tkinter python3-rpi.gpio

# Install Python dependencies
pip3 install -r requirements.txt

# Copy systemd service file
echo "Installing systemd service..."
cp ./systemd/batch-jig.service /etc/systemd/system/

# Update service file with correct paths (escape spaces in path)
sed -i "s|/home/qateam/Desktop/Project file|$PROJECT_DIR|g" /etc/systemd/system/batch-jig.service

# Set proper permissions
chown root:root /etc/systemd/system/batch-jig.service
chmod 644 /etc/systemd/system/batch-jig.service

# Enable and start the service
systemctl daemon-reload
systemctl enable batch-jig.service

# Configure auto-login for GUI applications
echo "Configuring auto-login..."
systemctl set-default graphical.target

# Enable auto-login to desktop
raspi-config nonint do_boot_behaviour B4

# Create desktop autostart entry as backup
mkdir -p /home/$SERVICE_USER/.config/autostart
cat > /home/$SERVICE_USER/.config/autostart/batch-jig.desktop << EOF
[Desktop Entry]
Type=Application
Name=Batch Jig
Comment=Automatic Cartridge Scanning JIG
Exec=python3 "$PROJECT_DIR/main.py"
Icon=applications-engineering
Terminal=false
Categories=Application;
StartupNotify=true
X-GNOME-Autostart-enabled=true
EOF

chown $SERVICE_USER:$SERVICE_USER /home/$SERVICE_USER/.config/autostart/batch-jig.desktop

echo ""
echo "✓ Auto-start setup complete!"
echo ""
echo "The jig will now automatically start when the Raspberry Pi boots."
echo ""
echo "Commands to manage the service:"
echo "  Start manually:    sudo systemctl start batch-jig"
echo "  Stop:             sudo systemctl stop batch-jig"  
echo "  Check status:     sudo systemctl status batch-jig"
echo "  View logs:        sudo journalctl -u batch-jig -f"
echo "  Disable auto-start: sudo systemctl disable batch-jig"
echo ""
echo "Reboot your Raspberry Pi to test the auto-start functionality."