# Jig Operation Synchronization Summary

## Hardware-Software Sync Overview

The batch validation jig operates with precise timing between the PIC firmware and Raspberry Pi software to ensure reliable cartridge sorting.

## 1. Startup Sequence

### PIC Firmware (main.c)
```
Power On → Hardware Init → PLC_STATE_SETUP
├── All actuators OFF
├── RJT_SNS sensor ready
├── LCD shows "Setup Batch"
└── Wait for Pi CMD_START_SCANNING ('B')
```

### Raspberry Pi (main.py)
```
Launch → Hardware Init → Setup UI
├── Assert RASP_IN_PIC HIGH (Pi ready)
├── Connect UART controller link
├── Show batch setup screen
└── Operator configures batch
```

## 2. Batch Start Transition

### Pi Action (start_scanning)
```
Operator clicks "Start Scanning"
├── Validate batch parameters
├── Create CSV logs
├── Send CMD_START_SCANNING ('B') to PIC
└── Show scanning UI
```

### PIC Response (CMD_START_SCANNING handler)
```
Receive 'B' → PLC_STATE_SCANNING
├── Enable all mechanical operations
├── LCD shows "Press Start"
└── Begin main scanning loop
```

## 3. Main Scanning Cycle

### Step A: Stack Check & Operator Start
**PIC Firmware:**
```
Check STACK_SNS sensor
├── If empty: LCD "Stack Empty, Fill Stack & Press Start"
├── Wait for stack refill
├── Wait for SW_3 (START button) press
└── Proceed to cartridge cycle
```

### Step B: Diverter Preparation
**PIC Firmware:**
```
Based on previous QR result:
├── Set REJECT_SV (0=Pass, 1=Reject)  
├── Wait for RJT_SNS confirmation (up to 6s)
├── If timeout: error_loop("REJECT PLT STUCK")
└── Diverter ready for next cartridge
```

### Step C: Cartridge Movement
**PIC Firmware:**
```
Move previous cartridge out:
├── PLATE_UD = 0 (raise plate)
├── CAT_FB = 0 (pusher backward)
├── Wait BW_SNS (10s timeout)
├── Wait MECH_UP_SNS (6s timeout)
├── Reset REJECT_SV = 0
└── Previous cartridge sorted

Feed new cartridge:
├── ELECT_SOL = 1 (stopper down)
├── CAT_FB = 1 (pusher forward)  
├── Wait FW_SNS (5s timeout)
├── ELECT_SOL = 0 (stopper up)
└── New cartridge at scan position
```

### Step D: QR Scan Request
**PIC Firmware:**
```
Send scan request to Pi:
├── uart_write_byte(CMD_RETRY/CMD_FINAL)
├── Wait for Pi response (12s timeout)
└── Receive result: 'A'=Pass, 'R'/'D'=Reject, 'S'=Skip
```

**Pi Response (_handle_controller_request):**
```
Receive scan request:
├── Set RASP_IN_PIC LOW (Pi busy)
├── Settle delay (20ms)
├── Start camera QR scan OR manual entry
├── Process QR code → status
├── Send result to PIC
└── Set RASP_IN_PIC HIGH (Pi ready)
```

### Step E: Result Processing
**PIC Firmware:**
```
Store result for next cycle:
├── prev_result = (0=Pass, 1=Reject)
├── Update counters
├── LCD display result
└── Loop back to Step B
```

## 4. Error Handling

### PIC Firmware (error_loop)
```
Any sensor timeout or stuck condition:
├── LCD shows specific error message
├── System halts all operations
├── Wait for operator SW_3 press
├── Clear error and continue
└── Ensures operator awareness
```

### Pi Software
```
UART timeout or communication error:
├── Log error message
├── Show error banner
├── Cancel pending operations
└── Continue monitoring for next request
```

## 5. Timing Constants (Synchronized)

| Constant | Value | Purpose |
|----------|--------|---------|
| T_CMD_MAX_WAIT_MS | 12000ms | Max Pi response time |
| T_BUSY_SETTLE_MS | 20ms | Hardware settle delay |
| T_CMD_PERIOD_MS | 20ms | UART poll interval |
| RJT_SNS_TIMEOUT | 6000ms | Diverter movement timeout |
| FW_SNS_TIMEOUT | 5000ms | Forward movement timeout |
| BW_SNS_TIMEOUT | 10000ms | Backward movement timeout |
| MECH_UP_SNS_TIMEOUT | 6000ms | Plate up timeout |

## 6. Pin Mapping (Hardware Interface)

| Pin | Function | Direction | Active |
|-----|----------|-----------|---------|
| RB6 | RASP_IN_PIC | PIC Input | HIGH=Ready |
| RC7/RC6 | UART RX/TX | Bidirectional | 115200 baud |
| RE2 | RJT_SNS | PIC Input | Plate position |
| RA4 | REJECT_SV | PIC Output | 1=Reject path |
| RC0/RC1 | BW_SNS/FW_SNS | PIC Input | Pusher position |
| RC2 | MECH_UP_SNS | PIC Input | Plate position |
| RC4 | STACK_SNS | PIC Input | Stack presence |
| RB4 | SW_3 | PIC Input | START button |

## 7. Real-Time Operation Flow

```
Pi: Batch started → Send 'B'
PIC: Enter scanning mode → Wait for stack + START
Operator: Fill stack, press START
PIC: Begin auto-cycle

Loop (while STACK_SNS active):
├── PIC: Set diverter for previous result
├── PIC: Move cartridge out → sort previous
├── PIC: Feed new cartridge → scan position
├── PIC: Request QR scan → Pi
├── Pi: Process QR → send result
├── PIC: Store result for next cycle
└── Repeat

Stack empty:
├── PIC: Display "Stack Empty, Fill & Start"
├── Operator: Refill stack, press START  
└── Resume auto-cycle
```

## Key Synchronization Points

1. **Batch Start**: Pi 'B' command enables PIC scanning mode
2. **QR Request**: PIC initiates, Pi responds within 12s
3. **Busy Signaling**: Pi asserts LOW during processing
4. **Error Recovery**: Both systems halt on errors, require operator intervention
5. **Timing**: All operations use matching timeout constants

This synchronized operation ensures reliable, safe cartridge sorting with full operator control and error visibility.