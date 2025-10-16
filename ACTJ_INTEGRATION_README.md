# ACTJ Integration Guide

## 🔗 **Mechanical Jig Integration with ACTJ Controller**

This document explains how to integrate your existing ACTJ jigs with the new QR validation system to create a fully automated, intelligent scanning jig.

## 🏗️ **System Architecture**

### **Hardware Components:**
1. **Existing ACTJ Controller (PIC18F4550)**
   - Handles all mechanical operations (pushers, cylinders, sensors)
   - Controls reject mechanisms and conveyor systems
   - Communicates via UART (115200 baud) with Raspberry Pi

2. **Raspberry Pi QR Validation System**
   - QR code scanning and validation
   - Batch tracking and duplicate detection
   - Data logging and cloud sync
   - Pass/reject decision making

3. **Shared Interface:**
   - Red/Green LED indicators (GPIO 20/21)
   - Small LCD display (I2C 0x27)
   - Buzzer for alerts (GPIO 23)

## 🔄 **Integration Flow**

### **Normal Operation Sequence:**
```
1. ACTJ detects cartridge in stack
2. ACTJ advances cartridge to scan position  
3. ACTJ signals Pi: "Ready for scan" (command 20/19)
4. Pi scans QR code and validates against batch
5. Pi sends result to ACTJ: A (accept) / R (reject)
6. ACTJ processes result:
   - PASS: Advance cartridge forward
   - REJECT: Divert to reject bin
7. ACTJ returns to step 1 for next cartridge
```

### **Communication Protocol:**

**Pi → ACTJ Commands:**
- `20` - Start QR scanning (with retry)
- `19` - Final QR scan attempt (no retry)
- `0` - Stop recording
- `23` - Start recording

**ACTJ → Pi Responses:**
- `A` - Cartridge accepted (PASS)
- `R` - Cartridge rejected (FAIL)
- `Q` - No QR code detected
- `S` - Scanner hardware error
- `H` - Hardware error
- `L` - QR length error
- `D` - Duplicate QR code
- `C` - Cartridge already tested
- `B` - Logging error

## 🔧 **Configuration**

### **UART Connection:**
```ini
# In settings_production.ini
[jig]
enabled = true
mechanical_integration = true
actj_uart_port = /dev/ttyS0
actj_baudrate = 115200
```

### **GPIO Pin Assignments:**
```
GPIO 20 → Red LED (Reject indication)
GPIO 21 → Green LED (Pass indication) 
GPIO 23 → Buzzer
Pin 39  → Ground (shared)
```

### **I2C LCD Display:**
```
Address: 0x27
Size: 16x2
Shows: Welcome, batch info, scan status
```

## 📁 **Key Integration Files**

### **`actj_integration.py`** - Main integration module
- `ACTJController` - UART communication with PIC controller
- `MechanicalJigInterface` - High-level mechanical operations
- `ACTJCommands/Responses` - Protocol definitions

### **Modified `main.py`** - Enhanced UI integration
- `_setup_mechanical_integration()` - Initialize ACTJ connection
- `_on_mechanical_event()` - Handle mechanical jig events
- Enhanced QR scan handling with mechanical feedback

### **`settings_production.ini`** - Production configuration
- UART settings for ACTJ communication
- GPIO pin assignments
- Mechanical integration flags

## 🚀 **Deployment Steps**

### **1. Hardware Setup:**
```bash
# Connect UART cable between Pi and ACTJ controller
# Pin connections:
#   Pi GPIO 14 (TXD) → ACTJ RX_PIC (RC7)  
#   Pi GPIO 15 (RXD) → ACTJ TX_PIC (RC6)
#   Pi GND → ACTJ GND

# Connect status LEDs and buzzer:
#   Pi GPIO 20 → Red LED + resistor → Ground
#   Pi GPIO 21 → Green LED + resistor → Ground  
#   Pi GPIO 23 → Buzzer + → Buzzer - to Ground
```

### **2. Software Configuration:**
```bash
# Switch to production mode
cd "/home/qateam/Desktop/Project file"
./switch_mode.sh prod

# Enable UART communication
sudo raspi-config
# → Interface Options → Serial Port
# → Enable serial interface, disable serial console

# Install auto-start
sudo ./install_autostart_simple.sh
```

### **3. Test Integration:**
```bash
# Test UART communication
sudo minicom -D /dev/ttyS0 -b 115200

# Test Pi application
python3 main.py

# Check logs
sudo journalctl -u batch-jig -f
```

## 🛠️ **Troubleshooting**

### **UART Communication Issues:**
```bash
# Check UART availability  
ls -la /dev/ttyS0

# Check permission
sudo usermod -a -G dialout qateam

# Test UART loopback
sudo minicom -D /dev/ttyS0 -b 115200
```

### **GPIO Issues:**
```bash
# Check GPIO access
sudo usermod -a -G gpio qateam
ls -la /dev/gpiomem

# Test LEDs manually  
echo 20 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio20/direction
echo 1 > /sys/class/gpio/gpio20/value  # Red LED on
echo 0 > /sys/class/gpio/gpio20/value  # Red LED off
```

### **Integration Debugging:**
```python
# Test ACTJ communication standalone
from actj_integration import ACTJController
actj = ACTJController("/dev/ttyS0", 115200)
actj.connect()
actj.send_command(ACTJCommands.START_SCAN)
response = actj.read_response()
print(f"Response: {response}")
```

## 📊 **Expected Benefits**

### **Quality Improvements:**
- ✅ **100% QR validation** - No invalid cartridges processed
- ✅ **Batch verification** - Only correct batch cartridges accepted  
- ✅ **Duplicate prevention** - Same cartridge can't be tested twice
- ✅ **Complete traceability** - Full audit trail maintained

### **Operational Benefits:**
- ✅ **Retrofit existing jigs** - No need to replace ACTJ hardware
- ✅ **Automated operation** - Minimal operator intervention
- ✅ **Real-time feedback** - Immediate pass/reject indication
- ✅ **Cloud integration** - Data automatically synced

### **Cost Benefits:**
- ✅ **Leverage existing investment** - ACTJ jigs remain functional
- ✅ **Add intelligence layer** - Pi system adds smart validation
- ✅ **Prevent rework** - Catch issues at test stage, not later
- ✅ **Improve yield** - Reduce false rejects through smart validation

## 🔍 **Validation Logic Integration**

Your existing QR validation logic is fully preserved:
- Batch number validation
- Line verification  
- Mould range checking
- Duplicate detection
- Format validation

The mechanical integration adds:
- Automatic cartridge positioning
- Physical pass/reject sorting  
- Visual feedback (LEDs)
- Continuous operation
- Error handling and recovery

## 📈 **Performance Monitoring**

The integrated system provides comprehensive logging:
- Scan rates and throughput
- Pass/reject statistics  
- Error frequencies
- Mechanical operation timing
- UART communication logs

This creates a complete **"Smart ACTJ"** that combines the reliability of your existing mechanical systems with intelligent QR validation and batch control! 🎯