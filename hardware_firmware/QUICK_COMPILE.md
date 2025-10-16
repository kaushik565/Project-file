# Quick Compilation Guide for MPLAB IPE

## For Immediate Hex File Creation

If you need the HEX file quickly, follow these minimal steps:

### Option 1: MPLAB X IDE (5 minutes)
1. **Open MPLAB X IDE**
2. **File → New Project**
   - Microchip Embedded → Standalone Project
   - Device: PIC18F4550
   - Compiler: XC8
   - Project Name: BatchFirmware

3. **Add Files:**
   - Source Files: Add `main.c`, `uart.c`, `lcd_i2c.c`
   - Header Files: Add all `.h` files from include/

4. **Set Include Path:**
   - Project Properties → XC8 → Preprocessing
   - Include Directories: Add path to `include/` folder

5. **Build:**
   - Click "Clean and Build" (hammer icon)
   - HEX file created in `dist/default/production/`

### Expected HEX File Location
```
YourProject/dist/default/production/BatchFirmware.production.hex
```

### Option 2: Command Line (Advanced)
```bash
# Navigate to firmware directory
cd hardware_firmware

# Compile with XC8
xc8-cc -mcpu=18f4550 src/*.c -Iinclude -o firmware.hex
```

## Critical Files Needed
Your firmware is ready to compile with these files:
- ✅ `src/main.c` - Main program (complete)
- ✅ `src/uart.c` - UART communication  
- ✅ `src/lcd_i2c.c` - LCD display
- ✅ `include/pins.h` - Pin definitions
- ✅ `include/config_bits.h` - PIC configuration
- ✅ `include/protocol.h` - Communication protocol
- ✅ All other headers complete

## Programming with MPLAB IPE
1. Open MPLAB IPE
2. Select Device: PIC18F4550  
3. Load your .hex file
4. Connect programmer and click "Program"

Your firmware is complete and ready for compilation! The HEX file will program your PIC18F4550 to communicate with the Raspberry Pi at 115200 baud and control all the hardware as specified.