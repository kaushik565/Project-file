# Complete Hardware Operation Sequence

## Overview
The new firmware implements the **exact same hardware operation sequence** as the old ACTJ firmware. All sensors, actuators, buttons, and timing are preserved. The **only change** is the addition of a batch setup state and communication with the new Pi app for QR validation.

---

## Detailed Operation Sequence (When START Button is Pressed)

### STEP 1: Stack Sensor Check
- **Check**: STACK_SNS sensor (RC4)
- **If empty (STACK_SNS = 0)**:
  - LCD shows "Stack Empty | Fill Stack &"
  - Waits until cartridges are loaded
  - Returns to "Press Start"
- **If cartridges present**: Continue to next step

### STEP 2: Wait for START Button
- **LCD shows**: "Press Start"
- **Waits for**: SW_3 button press (RB4, active low)
- **Debounce**: 50ms
- **Wait for release**: Ensures clean button press

### STEP 3: Cartridge Forward Movement
- **ELECT_SOL = 1**: Solenoid stopper DOWN (RA3)
  - Lowers stopper to allow cartridge to move
- **CAT_FB = 1**: Cartridge plate FORWARD (RE0)
  - Moves cartridge to scanning position
- **Wait 500ms**: Settle time
- **Check FW_SNS**: Forward sensor (RC1)
  - Timeout: 5000ms
  - If stuck: Show error, reset, and retry
- **ELECT_SOL = 0**: Stopper UP
- **Wait 500ms**: Settle time

### STEP 4: QR Scanning with Retry Logic
- **Increment count**: Total cartridges processed
- **Retry loop**: Up to 3 attempts
  
  **For each retry**:
  1. Send scan request to Pi via UART:
     - First 2 attempts: CMD_RETRY (0x14)
     - Final attempt: CMD_FINAL (0x13)
  2. **LCD shows**: "Reading QR | Hold steady..."
  3. Wait for Pi response (timeout: 12 seconds):
     - **'A' (ACCEPT)**: Pass → exit retry loop
     - **'R' (REJECT)**: Reject → exit retry loop
     - **'D' (DUPLICATE)**: Reject → exit retry loop
     - **'S' (SKIP)**: Retry → continue loop
  4. If no response or SKIP:
     - **LCD shows**: "Retrying"
     - Wait 500ms and try again

### STEP 5: Actuate Based on Result
- **If PASS (qr_result = 0)**:
  - REJECT_SV = 0 (RA4): Pass plate solenoid OFF
  - **LCD shows**: "PASS"
  - Increment pass_count
- **If REJECT/DUPLICATE/FAIL**:
  - REJECT_SV = 1 (RA4): Reject plate solenoid ON
  - **LCD shows**: "REJECT"
- **Wait 500ms**: Mechanical settle time

### STEP 6: Return Cartridge and Reset
- **PLATE_UD = 0**: Raise mech plate UP (RA2)
- **CAT_FB = 0**: Move cartridge plate BACKWARD (RE0)
  - Returns cartridge to exit position
- **Check BW_SNS**: Backward sensor (RC0)
  - Timeout: 10000ms
  - If stuck: Show error
- **Check MECH_UP_SNS**: Mech plate up sensor (RC2)
  - Timeout: 6000ms
  - If stuck: Show error
- **REJECT_SV = 0**: Reset reject solenoid
- **Wait 250ms**: Final settle time

### STEP 7: Loop Back
- Returns to STEP 1 (check stack sensor)
- Ready for next cartridge

---

## Pin Mapping (Same as Old Firmware)

### Inputs (Sensors & Buttons)
| Pin | Function | Description |
|-----|----------|-------------|
| RB3 | SW_2 | Menu button (active low) |
| RB4 | SW_3 | **START button** (active low) |
| RC4 | STACK_SNS | Stack sensor (cartridges present) |
| RC5 | CAT_SNS | Cartridge sensor |
| RC0 | BW_SNS | Backward sensor |
| RC1 | FW_SNS | Forward sensor |
| RC2 | MECH_UP_SNS | Mech plate up sensor |
| RB6 | RASP_IN_PIC | Pi BUSY signal |

### Outputs (Actuators)
| Pin | Function | Description |
|-----|----------|-------------|
| RA4 | REJECT_SV | Reject solenoid (1=reject, 0=pass) |
| RE0 | CAT_FB | Cartridge forward/backward (1=fwd, 0=bck) |
| RA2 | PLATE_UD | Mech plate up/down (0=up, 1=down) |
| RA3 | ELECT_SOL | Stopper solenoid (1=down, 0=up) |

### Communication
| Pin | Function | Description |
|-----|----------|-------------|
| RC6 | TX_PIC | UART TX to Pi |
| RC7 | RX_PIC | UART RX from Pi |

---

## Timing Summary (Same as Old Firmware)

| Operation | Timeout/Delay |
|-----------|--------------|
| Stack check poll | 100ms |
| Button debounce | 50ms |
| Stopper settle | 500ms |
| Forward sensor timeout | 5000ms (5s) |
| QR scan wait | 12000ms (12s) per attempt |
| Retry delay | 500ms |
| Result display | 500ms |
| Backward sensor timeout | 10000ms (10s) |
| Mech up sensor timeout | 6000ms (6s) |
| Final settle | 250ms |

---

## What's Different from Old Firmware?

### Removed
- ❌ Vacuum tests
- ❌ Valve tests
- ❌ USB functionality
- ❌ Temperature/ADC readings
- ❌ Service menu (can be added if needed)

### Added
- ✅ Batch setup state (waits for Pi "Start Scanning" command)
- ✅ Clean state machine (SETUP → SCANNING)
- ✅ Improved UART protocol with retry/final commands
- ✅ Better error handling and timeouts

### Preserved (100% Same)
- ✅ All pin assignments
- ✅ All sensor checks
- ✅ All actuator sequences
- ✅ All mechanical timings
- ✅ Retry logic (3 attempts)
- ✅ Stack empty detection
- ✅ Forward/backward movement
- ✅ Pass/reject sorting
- ✅ Error detection (stuck plates, timeouts)

---

## Summary

**The new firmware operates identically to the old firmware** in terms of hardware control. Every sensor, actuator, button press, and mechanical movement is preserved. The only additions are:

1. **Batch setup state**: Prevents operation until the Pi app is ready
2. **Enhanced Pi communication**: Better protocol for QR validation
3. **Cleaner code structure**: Easier to maintain and extend

**No hardware changes are required. All connections, timings, and operations remain the same.**
