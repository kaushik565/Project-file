#!/bin/bash

# Simple auto-start setup for existing project location
# Run this from your project directory: /home/qateam/Desktop/Project file

set -e

PROJECT_DIR="/home/qateam/Desktop/Project file"
SERVICE_USER="qateam"

echo "Setting up Automatic Cartridge Scanning JIG for auto-start..."
echo "Project directory: $PROJECT_DIR"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script as root (use sudo)"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "Error: main.py not found!"
    echo "Please run this script from your project directory:"
    echo "  cd '$PROJECT_DIR'"
    echo "  sudo ./install_autostart_simple.sh"
    exit 1
fi

echo "Installing required Python packages..."
apt-get update
apt-get install -y python3 python3-pip python3-tkinter python3-rpi.gpio

# Install Python dependencies
pip3 install -r requirements.txt

# Copy systemd service file
echo "Installing systemd service..."
cp ./systemd/batch-jig.service /etc/systemd/system/

# Set proper permissions
chown root:root /etc/systemd/system/batch-jig.service
chmod 644 /etc/systemd/system/batch-jig.service

# Enable and start the service
systemctl daemon-reload
systemctl enable batch-jig.service

# Configure auto-login for GUI applications
echo "Configuring auto-login..."
systemctl set-default graphical.target

# Enable auto-login to desktop (for qateam user)
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
echo "To switch to production mode (enable real hardware):"
echo "  ./switch_mode.sh prod"
echo ""
echo "Reboot your Raspberry Pi to test the auto-start functionality."