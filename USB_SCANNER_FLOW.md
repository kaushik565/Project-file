# Complete USB Scanner Operation Flow

## Real-World USB Scanner Integration

Your USB QR scanner integration works as follows:

### 1. **Hardware Setup**
- USB barcode/QR scanner connected to Raspberry Pi
- Scanner configured in "keyboard wedge" mode (sends keystrokes)
- Scanner programmed to send ENTER after each scan
- No special drivers needed - appears as USB HID keyboard

### 2. **Firmware-Pi Synchronization**
```
Firmware (PIC):                    Pi (main.py):
├── Position cartridge             
├── Hold with pins                 
├── Send CMD_RETRY/CMD_FINAL ────→ ├── Receive scan request
                                   ├── Set RASP_IN_PIC LOW (busy)
                                   ├── Enable QR entry field
                                   ├── Focus on QR input
                                   ├── Show "USB Scanner Ready"
                                   └── Wait for scanner input
USB Scanner triggered by operator
                                   ├── Scanner sends keystrokes
                                   ├── QR appears in entry field  
                                   ├── ENTER triggers _scan_qr_event
                                   ├── Validate QR code
                                   ├── Send result ('A'/'R'/'D') ─┐
                                   └── Set RASP_IN_PIC HIGH       │
├── Receive result ←────────────────────────────────────────────┘
├── Set diverter based on result
├── Move cartridge out → sorted
└── Feed next cartridge
```

### 3. **Timing Protection**
- **Pi waits max 11 seconds** for USB scanner input
- **Firmware waits max 12 seconds** for Pi response  
- **If timeout**: Pi sends 'S' (skip), firmware continues with next cartridge
- **Early scans ignored**: QR input only processed when firmware requests it

### 4. **USB Scanner Behavior**
```
Normal Operation:
├── Operator sees cartridge positioned
├── Operator triggers USB scanner (button press or auto-trigger)
├── Scanner reads QR code
├── Scanner sends QR text + ENTER to Pi
├── Pi processes immediately
└── Cycle continues

Error Cases:
├── Scanner triggers too early → QR ignored (firmware not ready)
├── Scanner triggers too late → Timeout, skip cartridge
├── Invalid QR format → Reject cartridge  
├── No scanner trigger → Timeout, skip cartridge
└── All cases allow jig to continue operation
```

### 5. **Operator Workflow**
1. **Setup**: Configure batch, click "Start Scanning"
2. **Jig**: Fill stack, press START button on jig hardware
3. **Auto-cycle begins**: Jig positions first cartridge
4. **Pi prompts**: "USB Scanner Ready - Scan QR code"
5. **Operator**: Trigger USB scanner (button/laser/auto)
6. **Result**: Pi shows PASS/REJECT, jig sorts cartridge
7. **Repeat**: Jig automatically feeds next cartridge
8. **Empty stack**: Jig stops, waits for refill + START

### 6. **Key Advantages**
- **Industrial reliability**: USB scanners are robust, fast
- **No timing issues**: Cartridge held steady by pins during scan
- **Fallback options**: Manual typing if scanner fails
- **Error recovery**: Timeouts don't stop the jig
- **Operator friendly**: Clear prompts and status display

### 7. **Scanner Configuration Requirements**
Most industrial USB scanners need these settings:
- **Mode**: Keyboard wedge (HID)
- **Suffix**: Carriage Return (CR) or ENTER  
- **Prefix**: None
- **QR Codes**: Enabled
- **Trigger**: Manual button or presentation mode

The system automatically handles all synchronization between the mechanical jig timing and the USB scanner input, ensuring reliable operation in production environments.