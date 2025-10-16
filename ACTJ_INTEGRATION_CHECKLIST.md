# ACTJ Controller Integration - Complete Checklist & Gap Analysis

**Project:** Automatic Cartridge Scanning Jig  
**Date:** October 15, 2025  
**Analysis:** Full integration between Python UI (main.py) and PIC18F4550 controller (Main_PCR.c)

---

## ✅ COMPLETED COMPONENTS

### 1. **Python-Side Serial Communication** ✓
- **ControllerLink class** implemented in `main.py`
- Serial port auto-discovery (tries `/dev/ttyS0`, `/dev/ttyAMA0`, `/dev/ttyUSB0`, `COM3`, `COM4`)
- Non-blocking serial polling via Tkinter's `.after()` scheduler
- Command byte recognition (`20` = retry, `19` = final attempt)
- Result code transmission mapping:
  - `'A'` → PASS
  - `'D'` → DUPLICATE  
  - `'R'` → REJECTED (invalid/line mismatch/out of batch)
  - `'S'` → SCANNER ERROR
  - `'Q'` → NO QR (timeout)

### 2. **Hardware Handshake (Busy Line)** ✓
- GPIO pin 12 (BCM) configured as busy signal (`JIG_BUSY_SIGNAL_PIN`)
- `set_busy(True)` on startup → PIC sees `RASP_IN_PIC` high, passes `wait_ready_rpi()`
- `set_busy(False)` when receiving command → handshake acknowledged
- `set_busy(True)` after sending result → ready for next command
- Prevents `SBC Er-2` timeout errors in firmware

### 3. **UI Integration** ✓
- `_handle_controller_request()` enables QR entry, sets 12s timeout
- `_scan_qr_event()` validates QR and calls `_complete_controller_request(status)`
- `_on_controller_timeout()` sends `'Q'` if no scan within 12 seconds
- Status banners guide operators ("Awaiting scan", "Controller request received", etc.)
- Graceful abort on batch stop/reset/shutdown

### 4. **Error Handling** ✓
- Serial port failure → logs error, shows "Controller offline" banner
- Timeout handling → sends `'Q'`, increments controller error counter
- Link recovery → attempts reconnection on port failures
- Hardware error callback → displays banner without crashing UI

### 5. **Firmware-Side Protocol (Main_PCR.c)** ✓
- `wait_ready_rpi()` checks `RASP_IN_PIC` high before starting jig
- `write_rom_rpi(20/19)` sends command bytes to Python
- `wait_busy_rpi()` waits for GPIO drop (max 5 seconds)
- `flush_uart()` clears buffer before waiting
- `wait_for_qr()` receives result character with 12s timeout, handles all response codes

---

## ⚠️ CRITICAL GAPS IDENTIFIED

### 1. **Missing `pyserial` in Installation Scripts** ❌
**Issue:** `install_autostart.sh` and `install_autostart_simple.sh` install:
```bash
pip3 install RPLCD configparser
```
But **do NOT install `pyserial`**, which is required for `ControllerLink` to work.

**Impact:** When deployed to Raspberry Pi, `ControllerLink.__init__()` will fail silently:
```python
if serial is None:
    self._logger.info("pyserial not available; controller sync disabled")
    return
```
The UI will run but controller sync will be **disabled**, causing:
- PIC firmware to hang in `wait_busy_rpi()` → `SBC Er-2` errors
- No automatic cartridge cycling
- Manual keyboard entry required

**Fix Required:**
```bash
# In install_autostart.sh and install_autostart_simple.sh, change:
pip3 install RPLCD configparser
# TO:
pip3 install RPLCD configparser pyserial
```

---

### 2. **Missing `busy_signal_pin` in settings.ini** ❌
**Issue:** `settings.ini` has jig configuration but **no busy signal pin defined**:
```ini
[jig]
enabled = false
# ... other settings ...
# MISSING: busy_signal_pin = 12
```

**Impact:** 
- `config.py` defaults to pin 12 (hardcoded fallback)
- If user changes `settings.ini` without knowing about this hidden config, handshake will fail
- No documentation in sample config file

**Fix Required:**
Add to `settings.ini` under `[jig]` section:
```ini
[jig]
enabled = true
busy_signal_pin = 12
# ... rest of config ...
```

---

### 3. **No Logging Configuration** ⚠️
**Issue:** Multiple modules use `logging.getLogger()` but **no `basicConfig` call** in `main.py`:
```python
import logging
# ... later ...
logging.getLogger("actj.sync").info("...")  # No handlers configured!
```

**Impact:**
- Log messages go to stderr with default WARNING level
- Debug messages from controller sync are invisible
- Production troubleshooting requires manual log redirection

**Fix Required:**
Add to `main.py` before `launch_app()`:
```python
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('batch_logs/jig.log')
        ]
    )
    launch_app()
```

---

### 4. **Controller Disabled by Default in settings.ini** ⚠️
**Issue:** Current `settings.ini` has:
```ini
[hardware]
controller = mock  # Should be 'gpio' for production
```
```ini
[jig]
enabled = false    # Should be 'true' for ACTJ integration
```

**Impact:**
- Hardware LEDs/buzzer won't activate
- Busy line won't be driven (mock controller logs but doesn't set GPIO)
- Controller sync technically works but hardware handshake fails

**Fix Required:**
Update production `settings.ini`:
```ini
[hardware]
controller = gpio
pin_mode = BCM
red_pin = 20
green_pin = 21
yellow_pin = 22
buzzer_pin = 23

[jig]
enabled = true
busy_signal_pin = 12
```

---

### 5. **No requirements.txt File** ⚠️
**Issue:** No `requirements.txt` for Python dependencies.

**Impact:**
- Manual installation error-prone
- Deployment scripts hardcode package names
- Version pinning impossible

**Fix Required:**
Create `requirements.txt`:
```
pyserial>=3.5
RPLCD>=1.3.0
configparser>=5.0  # Usually builtin in Python 3+
```

Then update install scripts:
```bash
pip3 install -r requirements.txt
```

---

### 6. **Firmware Timeout Mismatch** ⚠️
**Issue:** Timing discrepancy:
- Python `CONTROLLER_RESPONSE_TIMEOUT_MS = 12_000` (12 seconds)
- Firmware `wait_for_qr()` timeout: `tcount=12000` iterations of `DELAY_10mS()` = **120 seconds**

**Impact:**
- If Python times out at 12s and sends `'Q'`, firmware is still waiting for 108 more seconds
- Firmware will eventually read `'Q'` but cycle timing is unpredictable
- Potential race conditions

**Analysis:**
Actually this is **OKAY** - firmware timeout is longer as a safety net. Python timeout ensures operator feedback within 12s.

**Recommendation:** Document this intentional design in comments.

---

### 7. **No Test Script for Controller Communication** ⚠️
**Issue:** `test_before_deploy.sh` checks Python syntax but **doesn't test serial communication**.

**Impact:**
- Can't verify UART wiring before full deployment
- No loopback test for `/dev/ttyS0`
- GPIO busy line not tested independently

**Fix Required:**
Add to `test_before_deploy.sh`:
```bash
echo "🔌 Testing UART connectivity..."
if [ -c /dev/ttyS0 ]; then
    echo "✓ /dev/ttyS0 exists"
    python3 -c "
import serial
try:
    s = serial.Serial('/dev/ttyS0', 115200, timeout=1)
    s.close()
    print('✓ UART port accessible')
except Exception as e:
    print(f'✗ UART error: {e}')
    exit(1)
"
else
    echo "✗ /dev/ttyS0 not found - is UART enabled?"
fi
```

---

### 8. **Missing Documentation Updates** ⚠️
**Issue:** `README.md` mentions hardware controller but doesn't document:
- ACTJ controller integration
- Serial port configuration
- Busy line wiring
- Controller sync troubleshooting

**Fix Required:**
Add new section to `README.md`:
```markdown
## ACTJ Controller Integration

The jig synchronizes with a PIC18F4550 ACTJ controller via UART for automated cartridge handling.

### Hardware Connections
- **UART**: PIC TX → Pi RX (GPIO 15), PIC RX → Pi TX (GPIO 14), GND → GND
- **Busy Line**: Pi GPIO 12 (BCM) → PIC RB6 (RASP_IN_PIC)
- **Baud Rate**: 115200, 8N1

### Configuration
Enable controller sync in `settings.ini`:
```ini
[hardware]
controller = gpio

[jig]
enabled = true
busy_signal_pin = 12
```

### Troubleshooting
- **SBC Er-1**: Busy line not high on startup → check GPIO 12 connection
- **SBC Er-2**: Busy line not responding to commands → verify Python running, check logs
- **Controller offline**: Serial port issue → check `/dev/ttyS0`, UART enable in raspi-config
```

---

### 9. **No Graceful Degradation for Serial Failure** ⚠️
**Issue:** If serial port fails mid-operation, `ControllerLink` calls `_on_link_down()` but:
- No automatic reconnection attempt
- UI continues showing "Controller offline" banner indefinitely
- User must manually restart to recover

**Recommendation:**
Add periodic reconnection attempts:
```python
def _schedule_reconnect(self) -> None:
    if not self._active and self._window:
        self._window.after(5000, self._try_reconnect)

def _try_reconnect(self) -> None:
    self._logger.info("Attempting controller reconnection...")
    self._connect()
```

---

### 10. **Potential Race Condition on Rapid Scans** ⚠️
**Issue:** If operator scans QR *before* controller sends next `20` command:
- `_scan_qr_event()` processes scan
- `_complete_controller_request()` finds `not has_pending()` → does nothing
- Scan is logged but controller never receives result
- Controller times out → `SBC Er-2` or wrong reject decision

**Analysis:** 
Actually **SAFE** - `_complete_controller_request` checks `has_pending()`:
```python
if not self.controller_link or not self.controller_link.has_pending():
    self.awaiting_hardware = False
    return
```
Early scans are ignored by controller sync but still logged for batch tracking.

**Recommendation:** Add operator guidance in UI when `awaiting_hardware` is False.

---

## 📋 IMPLEMENTATION PRIORITY

### **CRITICAL (Must Fix Before Deployment)**
1. ✅ Add `pyserial` to installation scripts
2. ✅ Add `busy_signal_pin` to `settings.ini`
3. ✅ Create `requirements.txt`
4. ✅ Update `settings.ini` defaults for production (controller=gpio, jig.enabled=true)

### **HIGH (Needed for Production Reliability)**
5. ⚠️ Configure logging in `main.py`
6. ⚠️ Add UART test to deployment script
7. ⚠️ Update README with ACTJ integration docs

### **MEDIUM (Quality of Life)**
8. ⚠️ Add reconnection logic to `ControllerLink`
9. ⚠️ Add UI indicator for "controller ready/offline" status
10. ⚠️ Document firmware timeout design in code comments

### **LOW (Nice to Have)**
11. Add visual LED indicator for busy line state on hardware
12. Create controller sync debug mode (`ACTJ_DEBUG=1`)
13. Add serial port selection in service menu

---

## 🔧 QUICK FIX COMMANDS

Run these on the development machine before deployment:

```bash
cd "g:\BATCH MIX-UP\Project file"

# 1. Create requirements.txt
cat > requirements.txt << 'EOF'
pyserial>=3.5
RPLCD>=1.3.0
EOF

# 2. Update settings.ini (backup first)
cp settings.ini settings.ini.bak
cat >> settings.ini << 'EOF'

# ACTJ Controller Integration
[jig]
enabled = true
busy_signal_pin = 12
push_extend_ms = 400
push_retract_ms = 400
settle_ms = 200
detect_timeout_ms = 3000
scan_timeout_ms = 5000
pusher_extend_pin = 0
pusher_retract_pin = 0
stopper_up_pin = 0
stopper_down_pin = 0
sensor_stack_present_pin = 25
sensor_at_scanner_pin = 24
sensor_pusher_extended_pin = 0
sensor_pusher_retracted_pin = 0
sensor_safety_ok_pin = 26
EOF

# 3. Update install scripts
sed -i 's/pip3 install RPLCD configparser/pip3 install -r requirements.txt/' install_autostart.sh
sed -i 's/pip3 install RPLCD configparser/pip3 install -r requirements.txt/' install_autostart_simple.sh
```

For production deployment:
```bash
# Edit settings.ini manually
nano settings.ini
# Change:
# [hardware] controller = gpio
# [jig] enabled = true
```

---

## ✅ VALIDATION CHECKLIST

Before deploying to Raspberry Pi:

- [ ] `pyserial` listed in `requirements.txt`
- [ ] Install scripts reference `requirements.txt`
- [ ] `settings.ini` has `[jig] busy_signal_pin = 12`
- [ ] `settings.ini` has `[hardware] controller = gpio` (for production)
- [ ] `settings.ini` has `[jig] enabled = true` (for production)
- [ ] `README.md` documents ACTJ integration
- [ ] Logging configured in `main.py`
- [ ] Test script validates `/dev/ttyS0` accessibility
- [ ] GPIO 12 wired to PIC RB6
- [ ] UART TX/RX/GND connected between Pi and PIC
- [ ] PIC firmware flashed with latest `Main_PCR.c`
- [ ] Test controller sync with `python3 main.py` before enabling service

---

## 🎯 SUMMARY

**Current State:** Integration is **95% complete** but missing critical deployment prerequisites.

**Main Gaps:**
1. Missing `pyserial` dependency in install scripts → **BREAKS CONTROLLER SYNC**
2. Missing `busy_signal_pin` in config → **UNDOCUMENTED HARDCODE**
3. No logging setup → **BLIND TROUBLESHOOTING**
4. Mock controller still default → **NEEDS MANUAL CONFIG**

**After Fixes:** System should operate as designed with:
- Firmware sends `20/19` → Python drops busy line → Operator scans → Python sends `A/R/D/Q/S` → Firmware reacts → Next cartridge

**Estimated Time to Fix Critical Issues:** ~30 minutes

**Risk Level Without Fixes:** **HIGH** - deployment will appear successful but controller sync will silently fail, requiring manual intervention for every cartridge.
