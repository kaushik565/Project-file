# MPLAB X Project Configuration File
# Use this to create a new project in MPLAB X IDE

Device: PIC18F4550
Compiler: XC8 (recommended) or C18 (legacy)
Configuration: Production

## Project Structure:
```
hardware_firmware/
├── src/
│   ├── main.c           # Main firmware logic
│   ├── uart.c           # UART communication
│   └── lcd_i2c.c        # I2C LCD driver
├── include/
│   ├── config_bits.h    # Device configuration
│   ├── pins.h           # Pin definitions
│   ├── protocol.h       # Communication protocol
│   ├── uart.h           # UART header
│   ├── lcd_i2c.h        # LCD header
│   └── delay.h          # Delay functions
└── Makefile            # Command line build (optional)
```

## Compiler Settings:
- Optimization: Standard (-O1)
- Include Directories: include/
- Linker: Use default 18F4550 linker script
- Configuration Bits: Set in config_bits.h

## Output:
- Target: PIC18F4550
- Format: Intel HEX
- File: main.hex (for programming)