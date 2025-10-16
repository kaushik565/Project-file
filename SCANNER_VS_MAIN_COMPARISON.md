# SCANNER Project vs main.py - Complete Comparison

## Executive Summary

After detailed analysis, I found **3 CRITICAL MISSING FEATURES** in your main.py that exist in the SCANNER project:

1. ❌ **GPIO Pin 18 (SBC_BUSY_PIN) - NOT IMPLEMENTED**
2. ❌ **GPIO Pin 20 (TRIGGER_PIN) - NOT IMPLEMENTED**  
3. ❌ **GPIO Pin 21 (STATUS_PIN) - NOT IMPLEMENTED**

Your main.py only uses **GPIO 12** for the busy signal to PIC, but SCANNER uses **3 additional GPIO pins** for handshaking with the PIC controller!

---

## Detailed Hardware Comparison

### GPIO Pins Used

| Pin | SCANNER Project | Your main.py | Status | Purpose |
|-----|----------------|--------------|--------|---------|
| **GPIO 12** | ❓ Not visible | ✅ Used | **MATCH** | Busy line to PIC (RASP_IN_PIC) |
| **GPIO 18** | ✅ Used (`sbc_busy_pin`) | ❌ **MISSING** | **GAP!** | SBC busy indicator |
| **GPIO 20** | ✅ Used (`trigger_pin`) | ❌ **MISSING** | **GAP!** | Trigger input from PIC |
| **GPIO 21** | ✅ Used (`status_pin`) | ❌ **MISSING** | **GAP!** | Status output to PIC |

### Serial Connections

| Connection | SCANNER Project | Your main.py | Status |
|------------|----------------|--------------|--------|
| **UART to PIC** | ✅ `/dev/ttyS0` 115200 baud | ✅ `/dev/ttyS0` 115200 baud | ✅ **MATCH** |
| **Camera Scanner** | ✅ `/dev/qrscanner` 115200 | ✅ `/dev/qrscanner` 115200 | ✅ **MATCH** |

---

## Critical Analysis: GPIO Pin 18, 20, 21

### SCANNER Project Uses 3 Extra GPIO Pins

Looking at `SCANNER/matrix.py` lines 607-615:

```python
# SBC Busy Pin - GPIO 18 (output, always HIGH)
self.sbc_busy_pin = init_gpio(18, 'high')
set_gpio(self.sbc_busy_pin, 1)

if self.trig == True:  # If trigger mode enabled
    # Trigger Pin - GPIO 20 (input, waits for PIC signal)
    self.trigger_pin = init_gpio(20, 'in', 'rising')
    
    # Status Pin - GPIO 21 (output, tells PIC we're ready/busy)
    self.status_pin = init_gpio(21, 'high')
```

### What These Pins Do

#### **GPIO 18 - SBC_BUSY_PIN** 
```python
# Set HIGH when ready to receive commands
set_gpio(self.sbc_busy_pin, 1)

# Set LOW when processing
set_gpio(self.sbc_busy_pin, 0)
```

**Purpose**: Tells the PIC "Raspberry Pi is alive and ready"

#### **GPIO 20 - TRIGGER_PIN (Input)**
```python
# Wait for PIC to trigger a scan
poll_gpio(self.trigger_pin)  # Blocks until PIC raises GPIO 20

# Alternative: Read UART for trigger
uart_buf = self.uart.read(size=1)
if uart_buf[0] is 20:  # Command byte 20 from PIC
    break
```

**Purpose**: PIC can trigger scan via GPIO instead of (or in addition to) UART

#### **GPIO 21 - STATUS_PIN (Output)**
```python
# Before waiting for trigger
set_gpio(self.status_pin, 1)  # "I'm ready for trigger"
set_gpio(self.sbc_busy_pin, 1)

# After trigger received
set_gpio(self.status_pin, 0)  # "I'm busy scanning"
set_gpio(self.sbc_busy_pin, 0)
```

**Purpose**: Real-time status feedback to PIC during scan cycle

---

## Protocol Comparison

### SCANNER Handshake Sequence (FULL VERSION)

```
1. Raspberry Pi boots
   ├─ GPIO 18 (sbc_busy_pin) → HIGH
   ├─ GPIO 21 (status_pin) → HIGH  
   └─ Waits for trigger

2. PIC ready to scan
   ├─ Checks GPIO 18 is HIGH (Pi alive?)
   ├─ Checks GPIO 21 is HIGH (Pi ready?)
   └─ Either:
       Option A: Raises GPIO 20 (trigger_pin)
       Option B: Sends UART byte 20

3. Raspberry Pi receives trigger
   ├─ GPIO 21 (status_pin) → LOW
   ├─ GPIO 18 (sbc_busy_pin) → LOW
   └─ Camera starts scanning

4. QR detected
   ├─ Validates QR
   ├─ Sends result via UART ('A'/'R'/'D')
   ├─ GPIO 21 (status_pin) → HIGH
   └─ GPIO 18 (sbc_busy_pin) → HIGH

5. Ready for next cartridge (back to step 2)
```

### Your main.py Handshake (SIMPLIFIED VERSION)

```
1. Raspberry Pi boots
   └─ GPIO 12 → HIGH (busy line)

2. PIC ready to scan
   ├─ Checks GPIO 12 is HIGH
   └─ Sends UART byte 20

3. Raspberry Pi receives UART command
   ├─ GPIO 12 → LOW (drops busy line)
   └─ Camera starts scanning

4. QR detected
   ├─ Validates QR
   ├─ Sends result via UART ('A'/'R'/'D')
   └─ GPIO 12 → HIGH (raises busy line)

5. Ready for next cartridge
```

---

## Why Are GPIO 18/20/21 Missing?

### Possible Reasons

1. **Different PIC Firmware Version**
   - Your `Main_PCR.c` may not use these pins
   - SCANNER project might be for different hardware revision

2. **Simplified Protocol**
   - Your system uses ONLY UART + GPIO 12
   - SCANNER uses UART + GPIO 12 + GPIO 18/20/21 for redundancy

3. **Trigger Mode Disabled**
   - SCANNER has `trigger=True/False` mode
   - Your system always uses UART commands (no GPIO trigger)

---

## Do You NEED These Pins?

### ✅ **Your System Works WITHOUT Them If:**

1. Your `Main_PCR.c` firmware ONLY uses:
   - UART `/dev/ttyS0` for commands
   - GPIO 12 (RB6 on PIC) for busy line
   
2. Your PIC does NOT check GPIO 18/20/21

3. You've successfully tested with current setup

### ❌ **You NEED Them If:**

1. Your PIC firmware checks GPIO 18 (SBC busy indicator)
2. Your PIC uses GPIO 20 to trigger scans (instead of UART)
3. Your PIC monitors GPIO 21 for status feedback
4. You're getting "SBC Er-X" errors related to GPIO pins

---

## How to Verify What Your PIC Uses

### Check Main_PCR.c for These Signals

```bash
# Search for GPIO pin references
grep -n "RB.*18\|RB.*20\|RB.*21\|GPIO.*18\|GPIO.*20\|GPIO.*21" ACTJv20\(RJSR\)/Main_PCR.c
```

<function_calls>
<invoke name="grep_search">
<parameter name="includePattern">ACTJv20(RJSR)/Main_PCR.c