# USB QR Scanner Integration Guide

## Overview

The batch validation system supports QR code input through multiple methods:
1. **USB Barcode Scanner** (most common for industrial use)
2. **USB Camera** with QR detection
3. **Manual keyboard entry** (fallback)

## USB Barcode Scanner Setup

### Hardware Connection
1. Connect USB QR/barcode scanner to Raspberry Pi USB port
2. Scanner should be configured for **keyboard wedge mode** (default for most scanners)
3. No additional drivers needed - scanner appears as HID keyboard device

### Scanner Configuration
Most USB scanners work out-of-the-box, but ensure:
- **Suffix**: Configure scanner to send **ENTER** after each scan
- **Prefix**: No prefix needed (leave empty)
- **QR Code Types**: Enable all QR code formats
- **Data Format**: Plain text output

### Timing Synchronization

The system works as follows:

```
1. Operator: Start batch → Pi sends CMD_START_SCANNING to firmware
2. Firmware: Enter scanning mode → wait for stack + START button
3. Operator: Fill stack, press START on jig
4. Firmware: Position cartridge → send scan request to Pi
5. Pi: Enable QR entry → await USB scanner input
6. USB Scanner: Scan QR → send to Pi as keyboard input
7. Pi: Process QR → send result to firmware  
8. Firmware: Set diverter → move cartridge → repeat cycle
```

### Key Points

#### Cartridge Positioning
- USB scanner only triggers **after firmware positions cartridge**
- Cartridge is held in place by mechanical pins during scan
- Safe to scan - no risk of cartridge movement

#### Input Validation  
- QR input only processed when firmware requests scan
- Invalid timing (scan without request) is ignored
- Timeout protection if no scan within 11 seconds

#### Multiple Input Methods
- USB scanner has priority (fastest)
- Manual keyboard entry as backup
- Both methods use same validation logic

## Camera Scanner Alternative

If using USB camera instead of barcode scanner:

```ini
[camera]
enabled = true
port = /dev/video0  # or appropriate camera device
```

## Configuration Files

### settings.ini
```ini
[camera]
enabled = false  # Disable if using USB scanner only

[hardware] 
controller = gpio  # Enable for real hardware
```

### USB Scanner Testing

1. Open terminal and type: `lsusb`
2. Look for scanner device (usually shows as HID device)
3. Test by scanning QR code in any text editor
4. Should produce text + ENTER keypress

## Troubleshooting

### Scanner Not Working
- Check USB connection
- Verify scanner is in keyboard wedge mode
- Test in text editor first
- Check scanner configuration for ENTER suffix

### Timing Issues  
- Scanner triggers too early: QR ignored (firmware not ready)
- Scanner triggers too late: Timeout error displayed
- Optimal: Scan within 2-10 seconds of positioning

### No QR Detection
- Check cartridge positioning (should be held by pins)
- Verify QR code quality and lighting
- Ensure scanner is configured for QR codes
- Try manual keyboard entry as backup

## Production Setup Recommendations

1. **Use USB barcode scanner** for reliability
2. **Mount scanner at fixed position** above scan area  
3. **Configure ENTER suffix** for automatic processing
4. **Test complete cycle** before production use
5. **Train operators** on scan timing and positioning

The system automatically handles the complexity of coordinating the USB scanner with the mechanical jig timing.