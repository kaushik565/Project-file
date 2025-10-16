# ACTJv20(RJSR) Legacy Hardware Integration Guide

## Overview

This guide helps you run the new batch validation software on your existing **ACTJv20(RJSR)** hardware with the original `Main_PCR.c` firmware.

### Problem Solved

- **SBC Er-1 Error**: Timeout waiting for Raspberry Pi ready signal
- **SBC Er-2 Error**: Timeout during firmware-Pi communication
- **Incompatibility**: New software vs old firmware communication protocols

### Root Cause

The old ACTJv20(RJSR) firmware expects specific GPIO handshaking:
- `RASP_IN_PIC` (RB6) signal from Raspberry Pi
- GPIO 12 (Pi) → RB6 (ACTJv20) connection required
- Firmware waits for HIGH/LOW sequences to proceed

## Quick Setup

### 1. Switch to Legacy Mode
```bash
python3 switch_mode.py legacy
```

### 2. Test Legacy Integration
```bash
# Test with mock hardware first
python3 test_actj_legacy.py --mock

# Test with real GPIO
python3 test_actj_legacy.py

# View GPIO pin mapping
python3 test_actj_legacy.py --gpio-map
```

### 3. Run Application
```bash
python3 main.py
```

## Hardware Connections

### Required GPIO Connection
```
Raspberry Pi GPIO 12 → ACTJv20(RJSR) RB6 (RASP_IN_PIC)
```

### Pin Mapping
| Raspberry Pi | ACTJv20(RJSR) | Function |
|--------------|---------------|----------|
| GPIO 12      | RB6 (Pin 39)  | RASP_IN_PIC |
| Ground       | Ground        | Common GND |

## Legacy Mode Features

### ✅ What Works
- **QR Code Validation**: Full validation with patterns and duplicates
- **USB Scanner Support**: Keyboard wedge mode QR scanning
- **Manual Operation**: Manual cartridge positioning
- **Status Logging**: Complete CSV logging and batch tracking
- **GPIO Handshaking**: Proper firmware communication

### ⚠️ Manual Operations Required
- **Cartridge Positioning**: Manual placement in scanning position
- **Jig Control**: Manual operation of mechanical movements
- **Timing**: Operator controls scan timing

### ❌ Disabled Features
- **Automatic Jig Control**: No automated cartridge movement
- **Camera Scanner**: USB scanner only
- **LCD Integration**: Display remains firmware-controlled

## Firmware Communication Protocol

### Startup Sequence
1. **Boot**: RASP_IN_PIC = LOW (not ready)
2. **Initialize**: RASP_IN_PIC = HIGH (ready)
3. **Normal**: RASP_IN_PIC = LOW (standby)

### QR Scanning Sequence
1. **Prepare**: RASP_IN_PIC = HIGH (ready for QR)
2. **Process**: QR validation and logging
3. **Complete**: RASP_IN_PIC = LOW (busy/done)

### Error Prevention
- **SBC Er-1**: Prevented by proper startup HIGH signal
- **SBC Er-2**: Prevented by proper LOW signal after processing

## Configuration Files

### settings_legacy.ini
```ini
[hardware]
controller = gpio          # Enable GPIO for handshaking
pin_mode = BCM            # Use BCM pin numbering

[jig]
enabled = false           # Disable automated jig control
auto_start = false        # Manual operation only

[camera]
enabled = false           # Use USB scanner only

[window]
app_title = AUTOMATIC CARTRIDGE SCANNING JIG [LEGACY MODE]
```

## Troubleshooting

### SBC Er-1 Error
**Cause**: Firmware timeout waiting for Pi ready signal
**Solution**: 
- Check GPIO 12 connection to RB6
- Verify legacy mode is active
- Test with `python3 test_actj_legacy.py`

### SBC Er-2 Error  
**Cause**: Firmware timeout during QR scan communication
**Solution**:
- Ensure proper handshaking sequence
- Check GPIO signal integrity
- Verify legacy integration is working

### USB Scanner Not Working
**Cause**: Scanner device permissions or connection
**Solution**:
- Check scanner appears as keyboard device
- Test scanner with text editor first
- Verify USB connection

### Application Startup Issues
**Cause**: GPIO permissions or missing dependencies
**Solution**:
```bash
# Check GPIO permissions
sudo usermod -a -G gpio $USER

# Install dependencies
pip3 install -r requirements.txt

# Test hardware access
python3 test_actj_legacy.py --mock
```

## Testing Procedures

### 1. Hardware Test
```bash
# Test GPIO handshaking
python3 test_actj_legacy.py

# Expected output:
# ✓ Hardware controller: GPIOHardwareController
# ✓ RASP_IN_PIC set to LOW/HIGH
# ✓ Legacy integration active
# ✓ All sequences completed
```

### 2. QR Scanner Test
```bash
# Test in legacy mode
python3 main.py

# Scan test QR codes:
# MVANC00001, MVELR00014, etc.
# Should see successful validation
```

### 3. Firmware Communication Test
1. Power on ACTJv20(RJSR) hardware
2. Connect GPIO 12 to RB6
3. Start application
4. Should see no SBC errors on display
5. Place cartridge in scanning position
6. Scan QR code - should validate correctly

## Manual Operation Workflow

### Batch Setup
1. Run `python3 main.py`
2. Enter batch details in application
3. Select line and batch number
4. Click "Start Batch"

### Cartridge Processing
1. **Manual**: Place cartridge in scanning position
2. **Scan**: Use USB QR scanner on cartridge
3. **Validate**: Application validates and logs
4. **Manual**: Remove cartridge
5. **Repeat**: For next cartridge

### Batch Completion
1. Click "End Batch" when complete
2. Review logs in `batch_logs/` folder
3. Check setup logs in `Batch_Setup_Logs/`

## Files Created

### Core Integration
- `actj_legacy_integration.py` - Legacy hardware interface
- `settings_legacy.ini` - Legacy configuration
- `test_actj_legacy.py` - Testing utilities

### Modified Files
- `switch_mode.py` - Added legacy mode support
- `hardware.py` - Added RASP_IN_PIC GPIO control
- `logic.py` - Added legacy handshaking to QR processing
- `main.py` - Added legacy startup sequence

## Support

### Getting Help
1. Run diagnostic: `python3 diagnose_sbc2_error.py`
2. Check logs: `batch_logs/actj_legacy.log`
3. Test integration: `python3 test_actj_legacy.py`

### Common Issues
- **GPIO Permission**: Add user to gpio group
- **Pin Connection**: Verify GPIO 12 to RB6 wiring
- **Legacy Mode**: Ensure `switch_mode.py legacy` was run
- **USB Scanner**: Test scanner types text in text editor

### Success Indicators
- ✅ No SBC errors on hardware display
- ✅ QR codes validate correctly in application
- ✅ Batch logs created successfully
- ✅ Manual jig operation works normally

## Next Steps

1. **Test Setup**: `python3 test_actj_legacy.py`
2. **Switch Mode**: `python3 switch_mode.py legacy`
3. **Run Application**: `python3 main.py`
4. **Process Batches**: Manual operation with QR validation

Your ACTJv20(RJSR) hardware is now compatible with the new batch validation software!