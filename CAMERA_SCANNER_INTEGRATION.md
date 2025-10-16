# Camera QR Scanner Integration

## Overview

The `main.py` program now includes **automatic QR detection** using the same camera hardware from the SCANNER project. When a cartridge enters the scanning area, the camera automatically detects and reads the QR code without any manual intervention.

## Hardware Setup

### Required Hardware (Same as SCANNER Project)
- **Serial QR Camera Module** connected to `/dev/qrscanner`
- **Baud Rate**: 115200
- **Protocol**: Serial UART (same as SCANNER/matrix.py)
- **Trigger Command**: `[0x7E, 0x00, 0x08, 0x01, 0x00, 0x02, 0x01, 0xAB, 0xCD, 0x00]`

### Wiring
- Camera TX → Raspberry Pi RX (GPIO 15)
- Camera RX → Raspberry Pi TX (GPIO 14)
- Camera GND → Pi GND
- Camera VCC → Pi 5V

## Operation Flow

### Automatic Scanning Sequence

```
1. PIC controller detects cartridge at scan position
   ↓
2. PIC sends command byte (20 or 19) to Raspberry Pi via /dev/ttyS0
   ↓
3. Python ControllerLink receives command, calls _handle_controller_request()
   ↓
4. CameraQRScanner.start_scanning() triggered automatically
   ↓
5. Camera continuously captures images, decodes QR codes
   ↓
6. When QR detected: _on_camera_qr_detected(qr_code) called
   ↓
7. QR validation runs (batch check, duplicate check, format check)
   ↓
8. Result sent to PIC: 'A' (accept) / 'R' (reject) / 'D' (duplicate)
   ↓
9. PIC moves cartridge to accept/reject bin
   ↓
10. Next cartridge advances, cycle repeats
```

### No Manual Intervention Required! ✅

Unlike the previous manual entry method:
- **OLD**: Operator must point USB scanner and press Enter
- **NEW**: Camera automatically detects QR when cartridge is in position

## Configuration

### settings.ini

```ini
[camera]
enabled = true                # Enable automatic camera scanning
port = /dev/qrscanner        # Serial port for camera
baudrate = 115200            # Communication speed
timeout = 5                  # Read timeout in seconds
```

### Disabling Camera (Fallback to Manual)

If camera hardware is not available:

```ini
[camera]
enabled = false
```

The system will gracefully fall back to **manual QR entry** using keyboard/USB scanner.

## Code Architecture

### CameraQRScanner Class (main.py lines ~92-234)

```python
class CameraQRScanner:
    def __init__(self, port, on_qr_detected):
        # Initialize serial connection to camera
        
    def connect(self):
        # Open /dev/qrscanner serial port
        
    def start_scanning(self):
        # Launch background thread that continuously scans
        
    def _trigger_scan(self):
        # Send trigger command to camera
        # Read 7-byte response header
        # Read QR data (up to 50 bytes)
        # Return decoded QR string
        
    def _scan_loop(self):
        # Background thread: trigger → decode → callback
        # Stops after successful detection
        
    def close(self):
        # Cleanup serial connection
```

### Integration Points

**1. Initialization** (BatchScannerApp.__init__)
```python
self.camera_scanner = CameraQRScanner(
    port=CAMERA_PORT,
    on_qr_detected=self._on_camera_qr_detected
)
self.camera_scanner.connect()
```

**2. Automatic Start** (_handle_controller_request)
```python
def _handle_controller_request(self, final_attempt):
    # ... enable manual entry as fallback ...
    
    if self.camera_scanner:
        self.camera_scanner.start_scanning()  # Auto-scan!
```

**3. Detection Callback** (_on_camera_qr_detected)
```python
def _on_camera_qr_detected(self, qr_code):
    # Update UI entry field
    self.qr_entry.insert(0, qr_code)
    # Trigger validation immediately
    self._scan_qr_event(None)
```

**4. Cleanup** (_on_close)
```python
if self.camera_scanner:
    self.camera_scanner.close()
```

## Comparison: SCANNER vs main.py

| Feature | SCANNER/matrix.py | main.py |
|---------|-------------------|---------|
| Camera Port | `/dev/qrscanner` | `/dev/qrscanner` ✅ |
| Trigger Command | `0x7E...0xCD 0x00` | `0x7E...0xCD 0x00` ✅ |
| Response Check | `02 00 00 01 00 33 31` | `02 00 00 01 00 33 31` ✅ |
| Threading | PyQt5 QThread | Python threading ✅ |
| Integration | Standalone scanner | PIC controller sync ✅ |
| Validation | SQLite + CSV lookup | Batch + duplicate tracker ✅ |

## Testing

### Hardware Test (on Raspberry Pi)

```bash
# 1. Verify camera device exists
ls -l /dev/qrscanner

# 2. Test serial communication
python3 -c "import serial; s = serial.Serial('/dev/qrscanner', 115200); print('Camera OK')"

# 3. Run main.py
python3 main.py
```

### Expected Behavior

1. **On Startup**: Log shows `Camera QR scanner ready on /dev/qrscanner`
2. **When PIC sends command**: Log shows `Starting automatic camera scan`
3. **When QR detected**: Log shows `Camera detected QR: MVANC00001-015`
4. **Validation runs**: Accept/Reject/Duplicate logic executes
5. **Result sent to PIC**: GPIO drops, UART sends 'A'/'R'/'D'

### Troubleshooting

**Camera not detected**
```
WARNING: Camera scanner not available - using manual entry
```
- Check `/dev/qrscanner` exists: `ls -l /dev/qrscanner`
- Check permissions: `sudo chmod 666 /dev/qrscanner`
- Verify camera is connected and powered

**Camera timeout**
```
WARNING: Invalid response length: 0
```
- Camera may not be responding to trigger command
- Check wiring (TX/RX not swapped)
- Verify camera is configured for serial mode (not USB mode)

**QR too short**
```
WARNING: QR too short: 'ABC'
```
- QR code must be at least 10 characters
- Check camera focus and lighting
- Ensure QR is clear and undamaged

## Benefits

✅ **Fully Automatic**: No operator intervention needed  
✅ **Faster**: Immediate detection when cartridge enters scan area  
✅ **Consistent**: Same camera hardware as proven SCANNER project  
✅ **Reliable**: Automatic retry logic with PIC controller sync  
✅ **Fault Tolerant**: Falls back to manual entry if camera unavailable  

## System Integration Diagram

```
┌─────────────────┐
│ PIC18F4550      │ ← Mechanical control (pusher, sorter)
│ (Main_PCR.c)    │
└────────┬────────┘
         │ UART /dev/ttyS0
         │ GPIO 12 (busy line)
         │
┌────────▼───────────────────────┐
│ Raspberry Pi (main.py)         │
│                                │
│  ┌──────────────────────────┐ │
│  │ ControllerLink           │ │  ← Receives command byte 20/19
│  │  ↓ calls                 │ │
│  │ _handle_controller_req() │ │
│  └──────────┬───────────────┘ │
│             │                  │
│  ┌──────────▼───────────────┐ │
│  │ CameraQRScanner          │ │ ← Automatic scanning
│  │ - Sends trigger command  │ │
│  │ - Reads QR from camera   │ ◄──── /dev/qrscanner
│  │ - Calls callback         │ │      (Serial camera)
│  └──────────┬───────────────┘ │
│             │                  │
│  ┌──────────▼───────────────┐ │
│  │ _process_camera_qr()     │ │  ← Validation logic
│  │ - Batch check            │ │
│  │ - Duplicate check        │ │
│  │ - Send A/R/D to PIC      │ │
│  └──────────────────────────┘ │
└────────────────────────────────┘
```

## Next Steps

1. ✅ **Code Integration Complete**: CameraQRScanner class added to main.py
2. ✅ **Configuration Added**: settings.ini includes [camera] section
3. ⏳ **Hardware Deployment**: Connect camera to /dev/qrscanner on Raspberry Pi
4. ⏳ **End-to-End Test**: Load cartridges, press START, verify automatic scanning
5. ⏳ **Production Validation**: Test with 100+ cartridges to ensure reliability

---

**Status**: Ready for deployment to Raspberry Pi with camera hardware! 🎯
