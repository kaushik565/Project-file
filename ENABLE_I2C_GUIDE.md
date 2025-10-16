# Enable I2C on Raspberry Pi Guide

## Problem
Error: "could not open file /dev/i2c-1 no such file or directory"

This occurs when the I2C interface is disabled on the Raspberry Pi.

## Solution Steps

### Method 1: Using raspi-config (Recommended)
1. Open terminal on Raspberry Pi
2. Run configuration tool:
   ```bash
   sudo raspi-config
   ```
3. Navigate: **3 Interface Options** → **I2 I2C** → **Yes**
4. Exit raspi-config and reboot:
   ```bash
   sudo reboot
   ```

### Method 2: Manual Configuration
1. Edit boot configuration:
   ```bash
   sudo nano /boot/config.txt
   ```
2. Add or uncomment this line:
   ```
   dtparam=i2c_arm=on
   ```
3. Edit modules file:
   ```bash
   sudo nano /etc/modules
   ```
4. Add these lines if not present:
   ```
   i2c-dev
   i2c-bcm2708
   ```
5. Reboot the Pi:
   ```bash
   sudo reboot
   ```

### Method 3: Quick Enable Script
Create and run this script on the Pi:
```bash
#!/bin/bash
echo "Enabling I2C interface..."

# Enable I2C in config
sudo sed -i 's/#dtparam=i2c_arm=on/dtparam=i2c_arm=on/' /boot/config.txt
echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt

# Add I2C modules
echo "i2c-dev" | sudo tee -a /etc/modules
echo "i2c-bcm2708" | sudo tee -a /etc/modules

# Install I2C tools
sudo apt-get update
sudo apt-get install -y i2c-tools

echo "I2C enabled. Please reboot with: sudo reboot"
```

## Verification Steps

### 1. Check I2C Interface Exists
After reboot, verify I2C device exists:
```bash
ls -l /dev/i2c-*
```
Should show: `/dev/i2c-1`

### 2. Install I2C Tools
```bash
sudo apt-get install i2c-tools
```

### 3. Scan for I2C Devices
```bash
sudo i2cdetect -y 1
```
This should show your LCD at address 0x27 (or similar):
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- 27 -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --
```

### 4. Test I2C Communication
```bash
# Read from I2C device at address 0x27
sudo i2cget -y 1 0x27
```

## Common Issues & Solutions

### Issue: Permission Denied
Add user to i2c group:
```bash
sudo usermod -a -G i2c qateam
sudo usermod -a -G gpio qateam
```
Log out and back in.

### Issue: Wrong I2C Bus
Try i2c-0 instead of i2c-1:
```bash
sudo i2cdetect -y 0
```

### Issue: LCD Address Wrong
Scan for actual address:
```bash
sudo i2cdetect -y 1
```
Update `settings.ini` with correct address.

## Update Project Configuration

### For Development (Windows)
In `settings.ini`:
```ini
[LCD]
enabled = true
type = mock
```

### For Production (Raspberry Pi)
In `settings_production.ini`:
```ini
[LCD]
enabled = true
type = i2c
address = 0x27
```

## Deployment Script Addition

Add I2C enable check to deployment:
```bash
#!/bin/bash
# Check if I2C is enabled
if [ ! -e /dev/i2c-1 ]; then
    echo "Error: I2C not enabled!"
    echo "Run: sudo raspi-config -> Interface Options -> I2C -> Enable"
    echo "Then reboot and try again."
    exit 1
fi

echo "I2C interface verified ✓"
```

## Testing Steps

1. **Enable I2C** (using Method 1 above)
2. **Reboot Pi**
3. **Verify I2C device**: `ls /dev/i2c-*`
4. **Scan for LCD**: `sudo i2cdetect -y 1`
5. **Run your application**: `python main.py`

If LCD still shows mock mode, check your configuration file is using `type = i2c`.