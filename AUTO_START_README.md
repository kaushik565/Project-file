# Auto-Start Setup for Raspberry Pi

This guide explains how to set up your Automatic Cartridge Scanning JIG to automatically start when the Raspberry Pi boots up.

## Quick Setup (Recommended)

### Step 1: Copy Files to Raspberry Pi
```bash
# Navigate to your project directory
cd "/home/qateam/Desktop/Project file"

# Run the simple auto-start installation (requires sudo)
sudo ./install_autostart_simple.sh
```

### Step 2: Configure for Production
```bash
# Switch to production mode (enables real GPIO and LCD)
./switch_mode.sh prod

# Verify the configuration
./switch_mode.sh status
```

### Step 3: Reboot and Test
```bash
sudo reboot
```

## Manual Setup Instructions

If you prefer to set up auto-start manually:

### 1. Navigate to Project Directory
```bash
cd "/home/qateam/Desktop/Project file"
```

### 2. Install Dependencies
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-tkinter python3-rpi.gpio
sudo pip3 install RPLCD configparser
```

### 3. Install Systemd Service
```bash
sudo cp systemd/batch-jig.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable batch-jig.service
```

### 4. Configure Auto-Login
```bash
sudo systemctl set-default graphical.target
sudo raspi-config nonint do_boot_behaviour B4
```

### 5. Create Desktop Autostart (Backup Method)
```bash
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/batch-jig.desktop << EOF
[Desktop Entry]
Type=Application
Name=Batch Jig
Exec=python3 "/home/qateam/Desktop/Project file/main.py"
Terminal=false
Categories=Application;
StartupNotify=true
X-GNOME-Autostart-enabled=true
EOF
```

## Configuration Modes

### Development Mode (for testing)
```bash
./switch_mode.sh dev
```
- Uses mock hardware (no GPIO access required)
- Uses mock LCD (no I2C required)
- Safe for testing without hardware

### Production Mode (for real jig)
```bash
./switch_mode.sh prod
```
- Uses real GPIO pins (20=red, 21=green, 23=buzzer)
- Uses real I2C LCD (address 0x27)
- Enables jig automation features

## Service Management Commands

```bash
# Start the service manually
sudo systemctl start batch-jig

# Stop the service
sudo systemctl stop batch-jig

# Check service status
sudo systemctl status batch-jig

# View live logs
sudo journalctl -u batch-jig -f

# Disable auto-start (if needed)
sudo systemctl disable batch-jig

# Re-enable auto-start
sudo systemctl enable batch-jig
```

## Hardware Configuration

### GPIO Pin Assignments
- **GPIO 20**: Red LED (reject indication)
- **GPIO 21**: Green LED (pass indication)
- **GPIO 22**: Yellow LED (warning - optional)
- **GPIO 23**: Buzzer
- **Pin 39**: Ground (for LEDs and buzzer)

### LCD Display
- **Connection**: I2C (SDA/SCL pins)
- **Address**: 0x27 (configurable)
- **Size**: 16x2 characters
- **Purpose**: Shows welcome message, status, and batch info

### ASECT Controller PCB
- **Physical Pins 1-14**: Reserved for ASECT controller
- **GPIO 27**: Used by ASECT controller
- **Pusher Controls**: Handled by ASECT PCB (not Pi GPIO)

## Troubleshooting

### Service Won't Start
```bash
# Check the service status
sudo systemctl status batch-jig

# Check the logs
sudo journalctl -u batch-jig

# Check file permissions
ls -la "/home/qateam/Desktop/Project file/"
```

### Display Issues
```bash
# Check if running in graphical mode
echo $DISPLAY

# Check X11 permissions
xauth list

# Test display manually
DISPLAY=:0 python3 "/home/qateam/Desktop/Project file/main.py"
```

### GPIO Permissions
```bash
# Add user to gpio group
sudo usermod -a -G gpio qateam

# Check GPIO access
ls -la /dev/gpiomem
```

### LCD Not Working
```bash
# Check I2C is enabled
sudo raspi-config nonint do_i2c 0

# Scan for I2C devices
sudo i2cdetect -y 1

# Check RPLCD installation
python3 -c "from RPLCD.i2c import CharLCD; print('RPLCD OK')"
```

## File Structure

```
/home/qateam/Desktop/Project file/
├── main.py                 # Main application
├── config.py               # Configuration loader
├── settings.ini            # Current settings
├── settings.ini.sample     # Development settings
├── settings_production.ini # Production settings
├── jig.py                  # Jig controller
├── lcd_display.py          # LCD controller
├── hardware.py             # Hardware abstraction
├── logic.py                # Business logic
├── layout.py               # UI layout
├── duplicate_tracker.py    # Duplicate detection
├── systemd/
│   └── batch-jig.service   # Systemd service file
├── batch_logs/             # Scan logs
└── Batch_Setup_Logs/       # Setup logs
```

## Security Notes

- The service runs as user 'qateam' for security
- Auto-restart is enabled if the application crashes
- Logs are managed by systemd (automatic rotation)
- GPIO access requires proper permissions

## Testing

1. Test in development mode first: `./switch_mode.sh dev`
2. Run manually to check for errors: `python3 main.py`
3. Switch to production mode: `./switch_mode.sh prod`
4. Install auto-start: `sudo ./install_autostart_simple.sh`
5. Reboot and verify: `sudo reboot`