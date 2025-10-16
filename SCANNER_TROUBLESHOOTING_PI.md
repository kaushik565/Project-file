# USB Scanner Not Working on Raspberry Pi - Quick Fix Guide

## IMMEDIATE ACTIONS (try these first):

### 1. **Check USB Connection**
```bash
lsusb
```
Look for your scanner device. If not listed, try:
- Different USB port
- Different USB cable
- Reseat the connection

### 2. **Test Scanner in Simple Editor**
```bash
nano test.txt
```
- Click in the nano window
- Scan a QR code with your scanner
- Text should appear automatically
- Press Ctrl+X to exit

### 3. **Check User Permissions**
```bash
groups
```
You should see "input" in the list. If not:
```bash
sudo usermod -a -G input $USER
sudo usermod -a -G dialout $USER
```
Then **logout and login again**.

### 4. **Run Our Pi-Specific Test**
```bash
python3 test_pi_usb_scanner.py
```

### 5. **Quick Setup Script**
```bash
chmod +x setup_scanner_pi.sh
./setup_scanner_pi.sh
```

## COMMON ISSUES & SOLUTIONS:

### ❌ "Scanner not detected by lsusb"
- **Fix:** Check USB cable, try different port, scanner power
- **Test:** Unplug/replug scanner, check if LED lights up

### ❌ "Scanner detected but not typing"
- **Fix:** Scanner not in keyboard wedge mode
- **Test:** Check scanner manual for configuration barcodes
- **Solution:** Scan "USB HID Keyboard" configuration barcode

### ❌ "Permission denied" errors
- **Fix:** User not in input group
- **Solution:** 
  ```bash
  sudo usermod -a -G input $USER
  # Then logout and login
  ```

### ❌ "Scanner types but no ENTER"
- **Fix:** Configure scanner suffix
- **Solution:** Scan "Add CR/LF Suffix" configuration barcode

### ❌ "Works in nano but not in Python"
- **Fix:** Terminal focus issue
- **Solution:** Click in terminal window before scanning

## QUICK VERIFICATION:

1. **USB Detection:** `lsusb` shows scanner
2. **Permissions:** `groups` shows "input" 
3. **Basic Test:** Scanner types in `nano test.txt`
4. **Python Test:** Works in `python3 test_pi_usb_scanner.py`

## IF STILL NOT WORKING:

### Manual Configuration Steps:
1. Find scanner manual/documentation
2. Look for "USB HID" or "Keyboard Wedge" configuration
3. Scan the configuration barcode
4. Test again with nano

### Alternative Input Methods:
- Manual keyboard entry (always available)
- Different scanner model
- USB-to-serial adapter with serial scanner

### Get Help:
- Check scanner model number and manual
- Contact scanner manufacturer
- Post scanner model in support forum

---

**Most common fix: Add user to input group and logout/login!**