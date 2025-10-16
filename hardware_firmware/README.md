# ACTJ Hardware Firmware (from scratch)

This folder contains fresh, from-scratch firmware for the ACTJ jig controller (PIC MCU).
It is the only place for PLC/PIC sources, headers, build files, and the final HEX artifact.

## Goals

- Drive mechanics (feeder, pusher, reject/accept actuators)
- Read sensors (stack, presence, home switches)
- LCD UI (I2C 16x2) for operator states
- UART + BUSY GPIO handshake with Raspberry Pi

## Electrical interface (summary)

- UART: 115200 8N1, TTL levels (Pi GPIO14/15 ↔ PIC RX/TX)
- BUSY line: Pi GPIO12 → PIC RB6 (active-low to acknowledge a scan request)

## Protocol (see `include/protocol.h`)

- PIC emits 0x14 (20) to request scan (retry), 0x13 (19) for final attempt
- Pi drops BUSY low to acknowledge, performs QR, then sends ASCII code:
  - 'A' = Accept (PASS)
  - 'R' = Reject (invalid/mismatch)
  - 'D' = Duplicate
  - 'S' = Skip/Stop/Fallback
- PIC sorts according to result, raises ready state, updates LCD

## Build

Use Microchip toolchain (XC8/C18) compatible with your target (e.g., PIC18F4550).

Structure:

- `include/` headers
- `src/` C sources
- `Makefile` template (adjust device, tool paths)

## Flash

The build generates a `.hex`. Flash it to the controller with your programmer
(Pickit/ICD). Keep the `.hex` in this folder under a versioned name.

## Next steps

- Implement each TODO in `src/main.c` and driver modules.
- Tune timing constants in `include/protocol.h` to match mechanics.
- Validate with the Pi demo in `raspberry_pi_python/demo_handshake.py`.
