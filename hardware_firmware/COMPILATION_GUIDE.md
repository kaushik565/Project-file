# MPLAB X IDE Compilation Instructions

Follow these steps to compile your firmware and create the HEX file for MPLAB IPE programming:

## Method 1: Using MPLAB X IDE (Recommended)

### Step 1: Install MPLAB X IDE
1. Download MPLAB X IDE from Microchip website
2. Install XC8 Compiler (free version is sufficient)
3. Launch MPLAB X IDE

### Step 2: Create New Project
1. File → New Project
2. Choose "Microchip Embedded" → "Standalone Project" → Next
3. **Device**: Select "PIC18F4550" → Next
4. **Tool**: Select your programmer (PICkit 3/4, ICD, etc.) or "No Tool" → Next
5. **Compiler**: Select "XC8" → Next
6. **Project Name**: "BatchMixUpFirmware"
7. **Project Location**: Choose your directory → Finish

### Step 3: Add Source Files
1. Right-click "Source Files" in Project window → Add Existing Item
2. Add these files from `hardware_firmware/src/`:
   - main.c
   - uart.c
   - lcd_i2c.c

3. Right-click "Header Files" → Add Existing Item
4. Add these files from `hardware_firmware/include/`:
   - config_bits.h
   - pins.h
   - protocol.h
   - uart.h
   - lcd_i2c.h
   - delay.h

### Step 4: Configure Include Path
1. Right-click project name → Properties
2. Go to "XC8 Global Options" → "xc8-cc" → "Option Categories: Preprocessing and messages"
3. Add include path: `../include` or full path to your include directory
4. Click OK

### Step 5: Build Project
1. Click "Clean and Build" button (hammer + broom icon)
2. Check "Output" window for compilation results
3. If successful, you'll see: "BUILD SUCCESSFUL"

### Step 6: Locate HEX File
The compiled HEX file will be in:
```
YourProject/dist/default/production/BatchMixUpFirmware.production.hex
```

## Method 2: Using Command Line (Alternative)

### Requirements:
- MPLAB XC8 Compiler installed
- Command prompt/terminal

### Commands:
```bash
cd hardware_firmware
xc8-cc -mcpu=18f4550 -c src/main.c src/uart.c src/lcd_i2c.c -Iinclude
xc8-cc -mcpu=18f4550 -o firmware.hex main.o uart.o lcd_i2c.o
```

## Troubleshooting Common Issues

### Error: "Cannot find include file"
**Solution**: 
- Check include path settings
- Ensure all .h files are in include/ directory
- Verify file names match exactly

### Error: "Undefined symbols"
**Solution**:
- Ensure all .c files are added to project
- Check function names match between .c and .h files
- Verify all source files compile without errors

### Error: "Configuration bits"
**Solution**:
- Ensure config_bits.h is included
- Check PIC18F4550 device is selected correctly
- Verify configuration pragma statements

### Warning: "Function not prototyped"
**Solution**:
- Add function declarations to appropriate .h files
- Include necessary headers in source files

## Configuration Verification

Before programming, verify these settings in your project:

### Device Configuration:
- **Device**: PIC18F4550
- **Configuration**: Production
- **Optimization**: Standard (-O1)

### Compiler Settings:
- **Include Directories**: include/
- **Preprocessor**: Standard settings
- **Code Generation**: Default

### Memory Settings:
- **Program Memory**: 0x0000 - 0x7FFF
- **Configuration**: Use config_bits.h settings

## Programming with MPLAB IPE

Once you have the HEX file:

1. **Open MPLAB IPE**
2. **Select Device**: PIC18F4550
3. **Connect Programmer**: Choose your hardware programmer
4. **Load HEX File**: Browse to your .hex file
5. **Program**: Click "Program" button
6. **Verify**: Ensure programming successful

## Expected Output Files

After successful compilation:
- **firmware.hex** - Main programming file
- **firmware.map** - Memory map (optional)
- **firmware.lst** - Assembly listing (optional)

The .hex file is what you need for MPLAB IPE programming.

## Next Steps After Programming

1. **Connect Hardware**: UART, power, LCD, sensors
2. **Test UART**: Verify 115200 baud communication
3. **Test LCD**: Should show "WELCOME" on startup
4. **Connect Pi**: Establish UART link with Raspberry Pi
5. **Run Complete System**: Test with main.py application

Your firmware will be ready to communicate with the Raspberry Pi application once programmed successfully!