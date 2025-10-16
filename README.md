# Batch Scanning Jig

This repository contains the Tkinter UI, logging logic, and hardware adapters
for your cartridge-scanning jig. The application now reads its runtime options
from `settings.ini` and persists duplicate detection in `scan_state.db`.

## Quick Start Overview

1. On the Raspberry Pi run:
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-venv python3-pip git
   mkdir -p /home/pi/batch-jig
   ```
2. Copy the repository into `/home/pi/batch-jig`, then configure the app:
   ```bash
   cd /home/pi/batch-jig
   cp settings.ini.sample settings.ini
   nano settings.ini
   chmod +x start.sh
   ```
3. Test the UI:
   ```bash
   python3 main.py
   ```
4. (Optional) Enable auto-start for the UI:
   ```bash
   sudo systemctl daemon-reload
   # create /etc/systemd/system/batch-jig.service as described below
   sudo systemctl enable --now batch-jig.service
   ```
5. (Optional) Bring the log viewer online and make it reachable across the LAN:
   ```bash
   sudo SERVICE_USER=pi bash install_log_viewer_service.sh
   hostname -I  # browse to http://<pi-ip>:8080/
   ```

See the sections below for detailed explanations, troubleshooting tips, and
maintenance guidance.

## Configuration

1. Copy `settings.ini.sample` to `settings.ini`.
2. Adjust any values (header/footer text, folders, auto-advance, etc.).
3. Restart the application (`python3 main.py`) to pick up the changes.

Key `settings.ini` sections:

- `[ui]`: `header_text`, `footer_text`, `subheader_text`, `clock_format`, `auto_advance`
- `[window]`: `window_width`, `window_height`, `fullscreen`, `background_color`
- `[folders]`: `log_folder`, `setup_log_folder`, `recovery_file`
- `[layout]`: entry widths and padding (`entry_width`, `qr_width`, `padding_x`, `padding_y`, `section_gap`)
- `[typography]` and `[palette]`: fonts and colors for the 4.3" UI
- `[hardware]`: hardware controller selection (`controller = mock|gpio`), pin mode and GPIO pin numbers used by the status LEDs/buzzer.

## Running on Raspberry Pi

Follow these steps on a fresh Raspberry Pi OS install (Lite or Desktop).

### 1. Prepare the environment

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
```

- If you intend to drive GPIO hardware, open `sudo raspi-config` and enable the
  required interfaces (I2C/SPI) plus set timezone/keyboard as needed.
- Make sure your user (typically `pi`) owns the target project directory.

### 2. Copy the project onto the Pi
- Create a working folder:
  ```bash
  mkdir -p /home/pi/batch-jig
  ```
- Copy the repository contents into `/home/pi/batch-jig` (via `scp`, USB, or Git).
- Move into the project:
  ```bash
  cd /home/pi/batch-jig
  ```

### 3. Configure runtime settings

```bash
cp settings.ini.sample settings.ini
nano settings.ini  # or your preferred editor
```

- Adjust `[ui]` text, window size, and `[layout]` values to match your display.
- Set `[hardware] controller = gpio` and update pin numbers when running on a
  real jig; leave as `mock` for development.
- Review folder paths under `[folders]`; by default they stay inside the project.

### 4. Make scripts executable

```bash
chmod +x start.sh cleanup_logs.sh
```

### 5. Test the UI manually

```bash
python3 main.py
```

- The Tkinter window should open on the Pi’s display.
- Perform a sample scan (or type data) to ensure CSV files land in `batch_logs/`.
- Press `Ctrl+C` in the terminal when finished; the app persists state automatically.

### 6. Launch via helper script (optional)

```bash
./start.sh
```

This runs `main.py` inside the project’s virtualenv (if present) and is the
entry point used by the systemd service.

### 7. Install a systemd service for auto-start (recommended)

Create `/etc/systemd/system/batch-jig.service`:

```ini
[Unit]
Description=Batch Scanning Jig UI
After=network.target
Wants=graphical.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/batch-jig
ExecStart=/home/pi/batch-jig/start.sh
Environment=DISPLAY=:0
Restart=on-failure

[Install]
WantedBy=graphical.target
```

Reload and enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable batch-jig.service
sudo systemctl start batch-jig.service
```

Verify it is running with `sudo systemctl status batch-jig.service`. On the next
boot the UI will start automatically. Apply configuration changes by editing
`settings.ini` and restarting the service:

```bash
sudo systemctl restart batch-jig.service
```

## Operating the jig UI

Once the system is configured and the Tkinter application is running (manually or via the service), use this guide to operate it confidently.

### Launch & idle state
- On launch you land on **Batch Setup**. The blue auto-advance indicator shows whether the cursor moves automatically after each valid entry.
- A hint label beneath the title keeps you informed about the next focus target when auto-advance is active; when disabled it reminds you to press Tab or tap instead.

### Batch setup workflow
1. **Batch Number** – Scan or type the batch identifier (example: `MVANC00001`). Invalid input is highlighted in soft red until corrected.
2. **Batch Line** – Enter the production-line letter (single alphabet). Validation and highlighting mirror the batch-number field.
3. **Number of Moulds** – Enter the total mould types to configure, then click **Create Mould Fields**.
4. For each mould card (rendered with dividers and helper text):
   - Provide the mould **Name / Code** (three-character code – first alpha, remaining alphanumeric).
   - Enter the inclusive **QR Start** and **QR End** range for that mould. Each entry is validated against the batch line and mould name.
5. Click **Start Scanning** to generate the setup CSV in `Batch_Setup_Logs/` and transition to the scanning view.

### Scanning workflow
- The header shows the active batch and last scanned QR; the status label changes colour based on scan outcome.
- **Counters** for Accepted, Duplicate, and Rejected display totals “Since last reset.”
- A contextual banner appears after every scan (for roughly four seconds) describing the next action – e.g., how to resolve duplicates or invalid formats.
- The QR entry is enabled and focused automatically. Auto-advance hints continue updating while you scan.
- The large stop button accepts **right-clicks only** to prevent accidental stops. A hint below it reminds users to right-click (or emulate a right-click via long-press if using touch). Confirming a stop closes the CSV, clears duplicate tracking for the batch, and returns to Batch Setup.
- The footer now shows batch/session details plus the **device IP address**, making it easy to confirm which jig is online.

### Duplicate detection & logging
- Every scan is written to `batch_logs/<batch>.csv` with timestamp, batch, mould, QR, and status.
- Accepted codes are recorded in `scan_state.db`; re-scanning the same code during a batch triggers a **Duplicate** banner and increments the duplicate counter.
- Stopping a batch resets the counters and clears duplicate entries for that batch, while leaving other batches unaffected.

### Recovery behaviour
- The app stores recovery data (`recovery.json`) whenever a batch is live. On restart it offers to resume with the saved mould setup, counters, and last status.
- Cancelling the resume prompt or completing the batch clears the recovery file automatically.

### Troubleshooting tips
- **Invalid highlight persists** – Correct the highlighted field; the colour reverts to black once validation succeeds.
- **Line mismatch / out of batch** – Verify the batch line and mould QR ranges match the printed codes.
- **Stop button unresponsive** – Ensure you are using a right-click; standard taps are ignored by design.
- **Banner not clearing** – It disappears after four seconds or whenever a new scan arrives.

---

## ACTJ Controller Integration & Mechanical Jig Guide

This system integrates your Raspberry Pi QR validation logic with the ACTJ mechanical jig (PIC18F4550 controller). All mechanical operations (pushers, cylinders, reject bins) are handled by the ACTJ controller, while the Pi manages QR validation, batch tracking, and result signaling.

### Hardware Connections
- **UART**: Pi GPIO 14/15 ↔ PIC RX/TX, GND ↔ GND
- **Busy Line**: Pi GPIO 12 (BCM) ↔ PIC RB6
- **LEDs/Buzzer**: GPIO 20 (Red), 21 (Green), 23 (Buzzer)
- **LCD**: I2C 0x27, 16x2

### Workflow
1. ACTJ advances cartridge to scan position
2. ACTJ signals Pi (UART command 20/19)
3. Pi scans QR, validates, sends result (A/R/D/Q/S)
4. ACTJ moves cartridge (accept/reject)

### Configuration
- Set `[hardware] controller = gpio` and `[jig] enabled = true` in `settings.ini`
- Pin assignments and UART port are configurable

---

## Automatic Camera QR Scanner

- Uses `/dev/qrscanner` camera (same as SCANNER project)
- Fully automatic QR detection—no manual entry required
- Trigger command and protocol match SCANNER firmware
- Non-blocking, runs in background thread
- Falls back to manual entry if camera unavailable
- Enable/disable via `[camera]` section in `settings.ini`

### Troubleshooting
- If camera not found, check `/dev/qrscanner` and permissions
- If QR detection fails, verify lighting, focus, and cartridge position
- Fallback to manual entry by disabling camera in config

---

## Deployment & Validation Checklist

- [ ] `pyserial` listed in `requirements.txt`
- [ ] Install scripts reference `requirements.txt`
- [ ] `settings.ini` has `[jig] busy_signal_pin = 12`
- [ ] `settings.ini` has `[hardware] controller = gpio` (for production)
- [ ] Logging configured in `main.py`
- [ ] Test script validates `/dev/ttyS0` accessibility
- [ ] GPIO 12 wired to PIC RB6
- [ ] UART TX/RX/GND connected between Pi and PIC
- [ ] PIC firmware flashed with latest `Main_PCR.c`
- [ ] Test controller sync with `python3 main.py` before enabling service

---

## Auto-Start Setup for Raspberry Pi

- Use `install_autostart_simple.sh` for quick setup
- Switch between development and production modes with `switch_mode.sh`
- Systemd service file included for auto-start
- Troubleshooting tips for service, display, GPIO, and LCD issues

---

## Troubleshooting & Maintenance

- **UART issues**: Check `/dev/ttyS0`, permissions, and wiring
- **GPIO issues**: Ensure user is in `gpio` group, check `/dev/gpiomem`
- **LCD issues**: Enable I2C, check address, test with RPLCD
- **Camera issues**: Check device, permissions, and fallback config
- **Logs**: View with `journalctl -u batch-jig -f` or in `batch_logs/`
- **Cleanup**: Use `cleanup_logs.sh` and systemd timer to prune old logs
- **Log viewer**: Run `log_viewer.py` for browser-based CSV access

---

## Key Features & Benefits

- 100% QR validation, batch verification, duplicate prevention
- Retrofit existing jigs—no hardware replacement needed
- Automated operation, real-time feedback, cloud integration
- Full traceability and audit trail

---

## File Structure & Security Notes

- All main files, config, logs, and scripts are described above
- Service runs as non-root user, auto-restarts on failure
- Logs are rotated automatically
- GPIO access requires proper permissions

---

## Performance & Testing

- Automatic camera scanning increases throughput and reduces errors
- Test in development mode first, then switch to production
- Use provided scripts and checklists for reliable deployment

---

## For More Details

All previous documentation files have been consolidated here for clarity. For advanced integration, hardware wiring, and troubleshooting, refer to the sections above.
