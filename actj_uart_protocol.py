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
import serial
import time
import threading
from typing import Optional

from hardware import get_hardware_controller


class ACTJv20UARTProtocol:
    """UART communication protocol for ACTJv20(RJSR) firmware."""
    
    def __init__(self, port="/dev/serial0", baudrate=115200):
        self.logger = logging.getLogger("actj_uart")
        self.hardware = get_hardware_controller()
        self.serial_port = None
        self.port = port
        self.baudrate = baudrate
        self.running = False
        self.listen_thread = None
        
        # QR validation callback
        self.qr_validator = None
        
        # QR input handling
        self._waiting_for_qr = False
        self._scan_start_time = 0
        
    def connect(self):
        """Connect to ACTJv20 UART port."""
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
        except Exception as e:
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
                if self.serial_port and self.serial_port.in_waiting > 0:
                    # Read command from ACTJv20
                    data = self.serial_port.read(1)
                    if data:
                        command = data.decode('ascii', errors='ignore')
                        self.logger.debug(f"Received ACTJv20 command: {repr(command)}")
                        self._handle_command(command)
                
                time.sleep(0.01)  # Small delay to prevent busy loop
                
            except Exception as e:
                self.logger.error(f"Error in ACTJv20 listen loop: {e}")
                time.sleep(0.1)
    
    def _handle_command(self, command):
        """Handle command from ACTJv20 firmware."""
        if command in ['2', '1', '0']:  # Commands 20, 19, 10, etc. come as individual chars
            # This is likely a scan command (20 = '2' + '0')
            # We need to read the next character to get the full command
            try:
                next_char = self.serial_port.read(1).decode('ascii', errors='ignore')
                full_command = command + next_char
                self.logger.info(f"ACTJv20 scan command: {full_command}")
                
                if full_command in ['20', '19']:  # Scan commands
                    self._handle_scan_command()
                elif full_command == '10':  # Some other command
                    self.logger.debug("ACTJv20 command 10 received")
                    
            except Exception as e:
                self.logger.error(f"Error reading full command: {e}")
        
        elif command == '0':  # Stop command
            self.logger.info("ACTJv20 stop command received")
            self._handle_stop_command()
    
    def _handle_scan_command(self):
        """Handle QR scan command from ACTJv20."""
        try:
            # Signal busy to firmware (RASP_IN_PIC LOW)
            self.hardware.signal_busy_to_firmware()
            self.logger.info("ACTJv20 scan command - signaling BUSY, waiting for QR input")
            
            # Set a flag that we're waiting for QR input
            self._waiting_for_qr = True
            self._scan_start_time = time.time()
            
            # The USB QR scanner will trigger _process_qr_input when QR is scanned
            # For now, we'll wait up to 30 seconds for QR input
            timeout = 30.0
            while self._waiting_for_qr and (time.time() - self._scan_start_time) < timeout:
                time.sleep(0.1)
            
            if self._waiting_for_qr:
                # Timeout - send scanner error
                self.logger.warning("QR scan timeout - sending scanner error")
                self.serial_port.write(b'S')  # Scanner error
            
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
            except:
                pass
    
    def process_qr_input(self, qr_code):
        """Process QR code input from USB scanner."""
        if not self._waiting_for_qr:
            self.logger.debug(f"Received QR {qr_code} but not waiting for input")
            return
        
        try:
            self.logger.info(f"Processing QR code: {qr_code}")
            
            # Use the QR validator to check the code
            if self.qr_validator:
                status, mould = self.qr_validator(qr_code)
                
                if status == "PASS":
                    response = 'A'  # Accept
                    self.logger.info(f"QR validation PASSED ({mould}) - sending Accept")
                else:
                    response = 'R'  # Reject  
                    self.logger.info(f"QR validation FAILED ({status}) - sending Reject")
            else:
                response = 'A'  # Default to accept if no validator
                self.logger.warning("No QR validator set - defaulting to Accept")
            
            # Signal busy before sending response (critical for ACTJv20 timing)
            self.hardware.signal_busy_to_firmware()
            time.sleep(0.1)  # Brief delay for firmware to register busy state
            
            # Send response to ACTJv20
            self.serial_port.write(response.encode('ascii'))
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
            
        except Exception as e:
            self.logger.error(f"Error processing QR input: {e}")
            try:
                self.serial_port.write(b'S')  # Scanner error
                self._waiting_for_qr = False
            except:
                pass
    
    def _handle_stop_command(self):
        """Handle stop command from ACTJv20."""
        self.logger.info("ACTJv20 stop command - setting ready state")
        self.hardware.signal_ready_to_firmware()


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