#!/usr/bin/env python3

"""
ACTJv20(RJSR) UART Communication Protocol

The ACTJv20 firmware expects BOTH GPIO handshaking AND UART communication:

1. GPIO Handshaking (RASP_IN_PIC):
   - HIGH = Pi ready for commands  
   - LOW = Pi busy processing

2. UART Protocol:
   - Firmware sends: '20' (scan command with retry), '19' (scan final attempt), '0' (stop)
   - Pi must respond: 'A' (accept/pass), 'R' (reject/fail), 'S' (scanner error)

3. Complete Flow:
   - Firmware: write_rom_rpi(20) → Pi via UART
   - Firmware: wait_busy_rpi() → Check RASP_IN_PIC goes LOW  
   - Pi: Process QR and set RASP_IN_PIC LOW (busy)
   - Pi: Send 'A' or 'R' response via UART
   - Pi: Set RASP_IN_PIC HIGH (ready)
   - Firmware: wait_for_qr() → Receive Pi response
   - Firmware: Advance cartridge based on result
"""

import logging
import time
import threading
from typing import Optional, Tuple

try:  # Optional dependency in development environments
    import serial  # type: ignore
    from serial import SerialException  # type: ignore
except Exception:  # pragma: no cover - pyserial not installed
    serial = None  # type: ignore
    SerialException = Exception  # type: ignore

from hardware import get_hardware_controller


class ACTJv20UARTProtocol:
    """UART communication protocol for ACTJv20(RJSR) firmware."""
    
    def __init__(self, port="/dev/serial0", baudrate=115200):
        self.logger = logging.getLogger("actj_uart")
        self.hardware = get_hardware_controller()
        self.serial_port: Optional[serial.Serial] = None  # type: ignore[name-defined]
        self.port = port
        self.baudrate = baudrate
        self.running = False
        self.listen_thread = None
        
        # QR validation callback
        self.qr_validator = None
        self._scan_request_callback = None
        
        # QR input handling
        self._waiting_for_qr = False
        self._scan_start_time = 0
        
    def connect(self):
        """Connect to ACTJv20 UART port."""
        if serial is None:
            self.logger.error("pyserial not installed - cannot open ACTJv20 UART port")
            return False

        try:
            self.serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1.0,
                bytesize=8,
                parity='N',
                stopbits=1
            )
            self.logger.info(f"Connected to ACTJv20 on {self.port}")
            return True
        except SerialException as e:  # type: ignore[name-defined]
            self.logger.error(f"Failed to connect to ACTJv20: {e}")
            return False

    def set_qr_validator(self, validator_func):
        """Set QR validation function that returns ('PASS'/'FAIL', mould)."""
        self.qr_validator = validator_func
    
    def start_listening(self):
        """Start listening for ACTJv20 commands."""
        if not self.serial_port:
            if not self.connect():
                return False
                
        self.running = True
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        self.logger.info("Started listening for ACTJv20 commands")
        return True
    
    def stop_listening(self):
        """Stop listening for ACTJv20 commands."""
        self.running = False
        if self.listen_thread:
            self.listen_thread.join(timeout=2.0)
        if self.serial_port:
            self.serial_port.close()
            self.serial_port = None
        self.logger.info("Stopped ACTJv20 communication")
    
    def _listen_loop(self):
        """Main listening loop for ACTJv20 commands."""
        while self.running:
            try:
                if self.serial_port and getattr(self.serial_port, "in_waiting", 0):
                    data = self.serial_port.read(1)
                    if not data:
                        continue

                    command = data[0]
                    self.logger.debug(
                        "Received ACTJv20 command byte: 0x%02X", command
                    )
                    self._handle_command(command)

                time.sleep(0.01)  # Small delay to prevent busy loop

            except Exception as e:
                self.logger.error(f"Error in ACTJv20 listen loop: {e}")
                time.sleep(0.1)

    def _handle_command(self, command: int) -> None:
        """Handle command from ACTJv20 firmware."""
        if command == 20:  # Start scan (with retry allowed)
            self.logger.info("ACTJv20 scan command received (retry allowed)")
            self._handle_scan_command(final_attempt=False)
        elif command == 19:  # Final scan attempt
            self.logger.info("ACTJv20 scan command received (final attempt)")
            self._handle_scan_command(final_attempt=True)
        elif command == 0:  # Stop command / end of recording
            self.logger.info("ACTJv20 stop command received")
            self._handle_stop_command()
        elif command == 23:  # Start recording request
            self.logger.debug("ACTJv20 start recording command received")
            self.hardware.signal_ready_to_firmware()
        elif command == 24:  # Bluetooth pairing or auxiliary command
            self.logger.debug("ACTJv20 auxiliary command 24 received")
        else:
            self.logger.debug("Unknown ACTJv20 command byte: %s", command)

    def _handle_scan_command(self, final_attempt: bool = False):
        """Handle QR scan command from ACTJv20."""
        try:
            # Signal busy to firmware (RASP_IN_PIC LOW)
            self.hardware.signal_busy_to_firmware()
            self.logger.info("ACTJv20 scan command - signaling BUSY, waiting for QR input")

            # Set a flag that we're waiting for QR input
            self._waiting_for_qr = True
            self._scan_start_time = time.time()

            # Notify the application so it can prepare the UI for scanning
            if self._scan_request_callback:
                try:
                    self._scan_request_callback(final_attempt)
                except Exception as callback_exc:
                    self.logger.error(f"Scan request callback error: {callback_exc}")

            # The USB QR scanner will trigger _process_qr_input when QR is scanned
            # For now, we'll wait up to 30 seconds for QR input
            timeout = 30.0
            while self._waiting_for_qr and (time.time() - self._scan_start_time) < timeout:
                time.sleep(0.1)

            if self._waiting_for_qr:
                # Timeout - send scanner error
                self.logger.warning("QR scan timeout - sending scanner error")
                self.serial_port.write(b'S')  # Scanner error
                self._waiting_for_qr = False

            # Always signal ready at the end
            time.sleep(0.1)
            self.hardware.signal_ready_to_firmware()
            self.logger.info("ACTJv20 scan complete - signaling READY")
            
        except Exception as e:
            self.logger.error(f"Error handling scan command: {e}")
            # Send error response
            try:
                self.serial_port.write(b'S')  # Scanner error
                self.hardware.signal_ready_to_firmware()
                self._waiting_for_qr = False
            except:
                pass
    
    def process_qr_input(
        self,
        qr_code: str,
        validation_result: Optional[Tuple[str, Optional[str]]] = None,
    ) -> Tuple[Optional[str], Optional[str]]:
        """Process QR code input from USB scanner and respond to firmware."""
        if not self._waiting_for_qr:
            self.logger.debug(f"Received QR {qr_code} but not waiting for input")
            return None, None

        try:
            self.logger.info(f"Processing QR code: {qr_code}")

            # Use the QR validator to check the code
            if validation_result is not None:
                status, mould = validation_result
            elif self.qr_validator:
                status, mould = self.qr_validator(qr_code)
            else:
                status, mould = "PASS", None
                self.logger.warning("No QR validator set - defaulting to PASS")

            response = self._map_status_to_response(status)
            if response == 'A':
                self.logger.info(
                    "QR validation PASSED (%s) - sending Accept", mould or "UNKNOWN"
                )
            elif response == 'R':
                self.logger.info(
                    "QR validation FAILED (%s) - sending Reject", status
                )
            else:
                self.logger.info("QR validation produced error (%s) - sending error", status)

            # Signal busy before sending response (critical for ACTJv20 timing)
            self.hardware.signal_busy_to_firmware()
            time.sleep(0.1)  # Brief delay for firmware to register busy state

            # Send response to ACTJv20
            if not self.serial_port:
                raise RuntimeError("UART port is not connected")

            self.serial_port.write(response.encode('ascii'))
            if hasattr(self.serial_port, "flush"):
                try:
                    self.serial_port.flush()
                except Exception:  # pragma: no cover - serial flush not critical
                    pass
            self.logger.info(f"Sent response to ACTJv20: {response}")

            # ALL responses need proper GPIO pulse sequence for mechanism plate movement
            time.sleep(0.15)  # Wait for firmware to process the UART response

            if response == 'A':
                # Accept: Standard pulse sequence for mechanism plate
                self.hardware.signal_accept_pulse()
                self.logger.info("Sent ACCEPT GPIO pulse sequence for mechanism plate")

            elif response == 'R':
                # Reject: Extended pulse sequence for rejection path
                self.hardware.signal_rejection_pulse()  # Special rejection pulse sequence
                self.logger.info("Sent REJECT GPIO pulse sequence for mechanism plate")

            else:
                # Scanner error: Basic ready signal
                self.hardware.signal_ready_to_firmware()
                self.logger.info("Sent ERROR GPIO signal")

            # Final ready state after pulse sequence
            time.sleep(0.1)  # Allow mechanism to move
            self.hardware.signal_ready_to_firmware()

            # Clear the waiting flag
            self._waiting_for_qr = False

            return status, mould

        except Exception as e:
            self.logger.error(f"Error processing QR input: {e}")
            try:
                if self.serial_port:
                    self.serial_port.write(b'S')  # Scanner error
                self._waiting_for_qr = False
            except:
                pass
            return None, None

    def _handle_stop_command(self):
        """Handle stop command from ACTJv20."""
        self.logger.info("ACTJv20 stop command - setting ready state")
        self.hardware.signal_ready_to_firmware()

    def set_scan_request_callback(self, callback):
        """Register callback invoked when firmware requests a scan."""
        self._scan_request_callback = callback

    @property
    def is_waiting_for_qr(self) -> bool:
        """Expose whether the protocol is currently waiting for QR input."""
        return self._waiting_for_qr

    @staticmethod
    def _map_status_to_response(status: Optional[str]) -> str:
        """Translate validation status text to firmware response code."""
        if status == "PASS":
            return 'A'

        if status in {
            "DUPLICATE",
            "INVALID FORMAT",
            "LINE MISMATCH",
            "OUT OF BATCH",
            "REJECT",
            "FAIL",
        }:
            return 'R'

        return 'S'


# Integration with existing legacy system
_uart_protocol: Optional[ACTJv20UARTProtocol] = None


def get_uart_protocol() -> ACTJv20UARTProtocol:
    """Get singleton UART protocol instance."""
    global _uart_protocol
    if _uart_protocol is None:
        _uart_protocol = ACTJv20UARTProtocol()
    return _uart_protocol


def start_actj_communication(qr_validator_func=None):
    """Start ACTJv20 UART communication with QR validator."""
    protocol = get_uart_protocol()
    if qr_validator_func:
        protocol.set_qr_validator(qr_validator_func)
    if serial is None:
        protocol.logger.error(
            "pyserial not installed - cannot start ACTJv20 UART communication"
        )
        return False
    return protocol.start_listening()


def stop_actj_communication():
    """Stop ACTJv20 UART communication."""
    protocol = get_uart_protocol()
    protocol.stop_listening()


if __name__ == "__main__":
    # Test the UART protocol
    logging.basicConfig(level=logging.DEBUG)
    
    def test_qr_validator(qr_code):
        """Test QR validator function."""
        print(f"Validating QR: {qr_code}")
        return "PASS", "TEST_MOULD"
    
    protocol = ACTJv20UARTProtocol()
    protocol.set_qr_validator(test_qr_validator)
    
    if protocol.start_listening():
        print("ACTJv20 UART protocol test started")
        print("Send commands to test...")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping...")
            protocol.stop_listening()
    else:
        print("Failed to start ACTJv20 UART protocol")