# Raspberry Pi Python (from scratch)

This folder holds a clean, minimal adapter to talk to the PIC firmware and a demo harness.

## Modules

 `actj_link.py` — serial + BUSY GPIO handshake encapsulation
 `demo_handshake.py` — runs a loop that waits for PIC commands and replies with A/R/D

## Quick test

1. Wire UART and BUSY (GPIO12 -> RB6).
2. Run the demo:

   ```bash
   python3 demo_handshake.py
   ```

3. Watch the LCD and mechanics respond.

Integrate into your full UI later after bring-up.
