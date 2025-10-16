# Hardware & Pi Bring-up Checklist

## 1. Flashing the PIC/PLC Firmware
- Build the firmware in `hardware_firmware/` using MPLAB (C18 toolchain).
- Confirm config bits and pin mappings match your PCB.
- Flash the HEX file to the PIC18F4550 using a compatible programmer.

## 2. Wiring
- Connect UART (TX/RX) between Pi and PIC.
- Connect BUSY line (Pi GPIO12 → PIC RB6).
- Connect any additional handshake/status lines as per your schematic.
- All sensors, actuators, and LCD are managed by the PLC/PIC only.

## 3. Power-up Sequence
- Power on the PLC/PIC first; it will initialize hardware and display status on the LCD.
- Power on the Raspberry Pi; ensure it boots and launches the Python app.

## 4. Running the Pi App
- On the Pi, set `controller = gpio` in `settings.ini`.
- Run the app:

```powershell
python3 main.py
```

- The Pi will wait for scan requests from the PLC/PIC (protocol bytes 0x14/0x13).
- When a scan is requested, the Pi will validate the QR and send back the result code ('A', 'R', 'D', 'S').

## 5. Troubleshooting
- If the Pi app cannot connect to the serial port, check UART wiring and permissions.
- If QR validation fails, check the QR format and batch/mould settings in the UI.
- All hardware errors and LCD messages should be handled by the PLC/PIC firmware.

## 6. Optional: Test Handshake
- Use `raspberry_pi_python/demo_handshake.py` to simulate handshake and result codes for bench testing.

---
For further integration, keep all hardware logic in the PLC/PIC and only QR validation, logging, and UI in the Pi.
