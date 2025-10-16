# 🔧 Testing and Deployment Guide

## Phase 1: Local Testing (Windows Development)

### Step 1: Test Your Current Setup
```powershell
# In your current project folder
cd "G:\BATCH MIX-UP\Project file"

# Test the application in development mode
python main.py
```

**What to Check:**
- ✅ Application starts without errors
- ✅ UI loads properly with all buttons
- ✅ QR scanning works (try entering test QR codes manually)
- ✅ Batch setup functions work
- ✅ Logs are being created in `batch_logs/` folder

### Step 2: Test QR Validation Logic
```powershell
# Test with sample QR codes
# Start the app and enter these in QR field:

# Valid test codes (replace with your actual format):
MVANC00001
MVANC00002  
MVELR00014

# Invalid test codes:
INVALID123
WRONGFORMAT
```

**What to Verify:**
- ✅ Valid codes show "PASS" 
- ✅ Invalid codes show proper error messages
- ✅ Duplicate detection works
- ✅ Batch range validation works

### Step 3: Check Integration Files
```powershell
# Verify new files are created
dir *.py | findstr actj
dir *README.md
dir *.sh
```

**Expected Files:**
- `actj_integration.py` ✅
- `ACTJ_INTEGRATION_README.md` ✅  
- `install_autostart_simple.sh` ✅
- `settings_production.ini` ✅
- `switch_mode.sh` ✅

---

## Phase 2: Transfer to Raspberry Pi Jig

### Step 4: Copy Files to Raspberry Pi
```bash
# Method 1: Using SCP (if SSH is enabled)
scp -r "G:\BATCH MIX-UP\Project file\*" qateam@<PI_IP_ADDRESS>:"/home/qateam/Desktop/"

# Method 2: Using USB drive
# Copy entire "Project file" folder to USB
# Insert USB into Pi and copy to /home/qateam/Desktop/

# Method 3: Network share
# Share the folder over network and access from Pi
```

### Step 5: On Raspberry Pi - Initial Setup
```bash
# SSH into your Pi or use direct terminal
ssh qateam@<PI_IP_ADDRESS>

# Navigate to project directory  
cd "/home/qateam/Desktop/Project file"

# Make scripts executable
chmod +x *.sh

# Check Python dependencies
python3 -c "import tkinter, serial, logging, configparser; print('Dependencies OK')"
```

---

## Phase 3: Hardware Connection Testing

### Step 6: Test GPIO Connections (LEDs/Buzzer)
```bash
# Test RED LED (GPIO 20)
echo 20 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio20/direction  
echo 1 > /sys/class/gpio/gpio20/value    # Should turn RED LED ON
sleep 2
echo 0 > /sys/class/gpio/gpio20/value    # Should turn RED LED OFF

# Test GREEN LED (GPIO 21)
echo 21 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio21/direction
echo 1 > /sys/class/gpio/gpio21/value    # Should turn GREEN LED ON
sleep 2  
echo 0 > /sys/class/gpio/gpio21/value    # Should turn GREEN LED OFF

# Test BUZZER (GPIO 23)
echo 23 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio23/direction
echo 1 > /sys/class/gpio/gpio23/value    # Should make buzzer sound
sleep 1
echo 0 > /sys/class/gpio/gpio23/value    # Should stop buzzer

# Cleanup
echo 20 > /sys/class/gpio/unexport
echo 21 > /sys/class/gpio/unexport  
echo 23 > /sys/class/gpio/unexport
```

### Step 7: Test I2C LCD Connection
```bash
# Enable I2C
sudo raspi-config
# → Interface Options → I2C → Enable

# Scan for I2C devices
sudo i2cdetect -y 1
# Should show device at address 27 (0x27)

# Test RPLCD library
python3 -c "
from RPLCD.i2c import CharLCD
lcd = CharLCD('PCF8574', 0x27, cols=16, rows=2)
lcd.write_string('TEST MESSAGE')
print('LCD Test OK')
"
```

### Step 8: Test UART Connection to ACTJ
```bash
# Check UART device exists
ls -la /dev/ttyS0

# Test UART loopback (disconnect from ACTJ first)
# Connect Pi TXD to Pi RXD temporarily
echo "TEST" > /dev/ttyS0 &
cat /dev/ttyS0

# Test with ACTJ connected
sudo minicom -D /dev/ttyS0 -b 115200
# Type commands and see if ACTJ responds
```

---

## Phase 4: Software Testing

### Step 9: Test in Development Mode First
```bash
# Ensure development mode (mock hardware)
./switch_mode.sh dev
./switch_mode.sh status

# Run application
python3 main.py
```

**What to Test:**
- ✅ Application starts on Pi
- ✅ Touchscreen interface works  
- ✅ QR entry field accepts input
- ✅ Batch setup functions work
- ✅ Mock LCD shows debug messages in console

### Step 10: Test in Production Mode
```bash
# Switch to production mode (real hardware)
./switch_mode.sh prod
./switch_mode.sh status

# Run application with hardware
python3 main.py
```

**What to Test:**
- ✅ Real GPIO LEDs light up on pass/reject
- ✅ Real LCD displays welcome message
- ✅ Buzzer sounds for errors
- ✅ UART communication attempts (check logs)

---

## Phase 5: ACTJ Integration Testing

### Step 11: Test ACTJ Communication
```bash
# Test ACTJ integration module standalone
python3 -c "
from actj_integration import ACTJController
actj = ACTJController('/dev/ttyS0', 115200)  
if actj.connect():
    print('ACTJ Connected OK')
    # Send test command
    from actj_integration import ACTJCommands
    actj.send_command(ACTJCommands.START_SCAN)
    print('Command sent')
else:
    print('ACTJ Connection failed')
"
```

### Step 12: Full Integration Test
```bash
# Run application with ACTJ integration enabled
# Make sure ACTJ controller is powered and connected
python3 main.py

# In the application:
# 1. Set up a test batch
# 2. Enter scan mode  
# 3. Manually trigger QR scan
# 4. Watch for ACTJ responses
# 5. Check LED feedback
# 6. Verify mechanical actions
```

---

## Phase 6: Production Deployment

### Step 13: Install Auto-Start (Only After Testing)
```bash
# ONLY run this after confirming everything works manually
sudo ./install_autostart_simple.sh

# Check service status
sudo systemctl status batch-jig

# Test reboot behavior
sudo reboot
# Application should start automatically after boot
```

### Step 14: Monitor and Debug
```bash
# View real-time logs
sudo journalctl -u batch-jig -f

# Check application logs
tail -f /home/qateam/Desktop/"Project file"/batch_logs/*.csv

# Monitor system resources
htop

# Check GPIO usage
sudo cat /sys/kernel/debug/gpio
```

---

## 🔍 Troubleshooting Guide

### Common Issues and Solutions:

**Application won't start:**
```bash
# Check Python path and dependencies
which python3
python3 -c "import sys; print(sys.path)"
pip3 list | grep -E "(tkinter|serial|RPLCD)"
```

**GPIO permission denied:**
```bash
# Add user to gpio group
sudo usermod -a -G gpio qateam
# Logout and login again
```

**UART permission denied:**
```bash
# Add user to dialout group  
sudo usermod -a -G dialout qateam
# Check UART permissions
ls -la /dev/ttyS0
```

**LCD not working:**
```bash
# Check I2C is enabled
sudo raspi-config
# Check I2C address
sudo i2cdetect -y 1
# Test with different address if needed (0x3f, 0x26, etc.)
```

**ACTJ not responding:**
```bash
# Check physical connections
# Verify ACTJ power and firmware
# Test UART with oscilloscope/logic analyzer
# Check baud rate settings (115200)
```

---

## 📊 Success Criteria Checklist:

**Hardware Tests:**
- [ ] Red LED lights up on GPIO 20
- [ ] Green LED lights up on GPIO 21  
- [ ] Buzzer sounds on GPIO 23
- [ ] LCD shows messages clearly
- [ ] UART communication established

**Software Tests:**
- [ ] Application starts without errors
- [ ] QR validation works correctly
- [ ] Batch setup and tracking functions
- [ ] Logs are generated properly
- [ ] Mode switching works (dev/prod)

**Integration Tests:**  
- [ ] ACTJ controller responds to commands
- [ ] Mechanical operations trigger properly
- [ ] Pass/reject decisions control hardware
- [ ] Error handling works correctly
- [ ] Auto-start functions after reboot

**Production Readiness:**
- [ ] System runs stably for extended periods
- [ ] Error recovery works automatically  
- [ ] Logging and monitoring functional
- [ ] Operator interface is intuitive
- [ ] Performance meets production requirements

Once ALL these tests pass, your integrated smart jig is ready for production use! 🎯