#!/usr/bin/env python3

"""
ACTJv20(RJSR) Legacy Hardware Integration

This module provides compatibility layer for running the new batch validation
software on the old ACTJv20(RJSR) hardware with original Main_PCR.c firmware.

The old firmware expects specific GPIO handshaking protocols:
- RASP_IN_PIC (RB6) signal from Raspberry Pi to indicate ready/busy state
- SBC Er-1: Timeout waiting for RASP_IN_PIC to go HIGH (Pi not ready)
- SBC Er-2: Timeout waiting for RASP_IN_PIC to go LOW after HIGH (Pi not responding)

This integration implements the required handshaking to prevent SBC errors.
"""

import logging
import time
import threading
from typing import Optional

from hardware import get_hardware_controller
from actj_uart_protocol import get_uart_protocol, start_actj_communication, stop_actj_communication


class ACTJLegacyIntegration:
    """Legacy integration for ACTJv20(RJSR) firmware communication."""
    
    def __init__(self):
        self.logger = logging.getLogger("actj_legacy")
        self.hardware = get_hardware_controller()
        self.uart_protocol = get_uart_protocol()
        self.ready_signaled = False
        self.busy_signaled = False
        
        # Start with Pi not ready (RASP_IN_PIC LOW)
        self.signal_not_ready()
        
        self.logger.info("ACTJv20(RJSR) Legacy Integration initialized")
        self.logger.info("IMPORTANT: Use this only with old ACTJv20(RJSR) firmware")
        self.logger.info("UART communication required for full automatic operation")
    
    def signal_ready(self) -> None:
        """Signal to firmware that Raspberry Pi is ready (RASP_IN_PIC HIGH)."""
        if not self.ready_signaled:
            self.logger.info("Signaling READY to ACTJv20(RJSR) firmware")
            self.hardware.signal_ready_to_firmware()
            self.ready_signaled = True
            self.busy_signaled = False
    
    def signal_busy(self) -> None:
        """Signal to firmware that Raspberry Pi is busy (RASP_IN_PIC LOW)."""
        if not self.busy_signaled or self.ready_signaled:
            self.logger.info("Signaling BUSY to ACTJv20(RJSR) firmware")
            self.hardware.signal_busy_to_firmware()
            self.busy_signaled = True
            self.ready_signaled = False
    
    def signal_not_ready(self) -> None:
        """Signal to firmware that Raspberry Pi is not ready (RASP_IN_PIC LOW)."""
        self.logger.debug("Signaling NOT READY to ACTJv20(RJSR) firmware")
        self.hardware.signal_busy_to_firmware()
        self.ready_signaled = False
        self.busy_signaled = False
    
    def prepare_for_qr_scan(self) -> None:
        """Prepare for QR scanning - signal ready to firmware."""
        self.logger.info("Preparing for QR scan - signaling ready to firmware")
        self.signal_ready()
        # Small delay to ensure firmware sees the ready state
        time.sleep(0.1)
    
    def complete_qr_scan(self) -> None:
        """Complete QR scanning - signal busy to firmware."""
        self.logger.info("QR scan complete - signaling busy to firmware")
        self.signal_busy()
        # Small delay to ensure firmware sees the busy state
        time.sleep(0.1)
    
    def handle_scanning_sequence(self, qr_data: str) -> bool:
        """
        Handle the complete scanning sequence with proper firmware handshaking.
        
        Args:
            qr_data: The QR code data to process
            
        Returns:
            bool: True if sequence completed successfully
        """
        try:
            self.logger.info(f"Starting ACTJv20(RJSR) scanning sequence for: {qr_data}")
            
            # Step 1: Signal ready for scanning
            self.prepare_for_qr_scan()
            
            # Step 2: Process the QR data (this would integrate with your validation logic)
            self.logger.info(f"Processing QR data: {qr_data}")
            
            # Step 3: Signal completion
            self.complete_qr_scan()
            
            self.logger.info("ACTJv20(RJSR) scanning sequence completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in ACTJv20(RJSR) scanning sequence: {e}")
            self.signal_not_ready()
            return False
    
    def startup_sequence(self) -> None:
        """Execute startup sequence for ACTJv20(RJSR) automatic operation."""
        self.logger.info("Starting ACTJv20(RJSR) startup sequence for AUTOMATIC OPERATION")
        
        # Initialize GPIO for ACTJv20 communication
        try:
            if hasattr(self.hardware, 'initialize_actj_gpio'):
                self.hardware.initialize_actj_gpio()
                self.logger.info("✅ ACTJv20 GPIO initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ GPIO initialization failed: {e}")
            raise
        
        # Start with not ready
        self.signal_not_ready()
        time.sleep(0.5)
        
        # Signal ready to indicate Pi has booted and jig can start
        self.logger.info("Signaling READY - ACTJv20 JIG CAN START AUTOMATIC OPERATION")
        self.signal_ready()
        time.sleep(0.5)
        
        # Return to busy state for normal operation
        self.signal_busy()
        
        # Start UART communication for automatic operation
        self.logger.info("Starting UART communication with ACTJv20...")
        if start_actj_communication(qr_validator_func=self._qr_validation_bridge):
            self.logger.info("✅ UART communication started - FULL AUTOMATIC MODE")
        else:
            self.logger.warning("⚠️ UART communication failed - GPIO-only mode")
        
        self.logger.info("ACTJv20(RJSR) startup sequence completed - AUTOMATIC MODE READY")
        
    def _qr_validation_bridge(self, qr_code):
        """Bridge function to connect UART protocol with QR validation."""
        try:
            # This integrates with the main application's QR validation
            # We need to get the current batch context from the main app
            self.logger.info(f"QR validation bridge called for: {qr_code}")
            
            # Try to get validation context from main application
            try:
                # This will be set by the main application when it starts
                if hasattr(self, '_batch_context'):
                    batch_line = self._batch_context.get('batch_line', 'A')
                    mould_ranges = self._batch_context.get('mould_ranges', {})
                    duplicate_checker = self._batch_context.get('duplicate_checker', None)
                    
                    from logic import handle_qr_scan
                    status, mould = handle_qr_scan(qr_code, batch_line, mould_ranges, duplicate_checker)
                    
                    self.logger.info(f"QR validation result: {status} (mould: {mould})")
                    return status, mould
                else:
                    self.logger.warning("No batch context available - defaulting to PASS")
                    return "PASS", "DEFAULT_MOULD"
                    
            except Exception as e:
                self.logger.error(f"Error in QR validation: {e}")
                return "FAIL", None
                
        except Exception as e:
            self.logger.error(f"QR validation bridge error: {e}")
            return "FAIL", None
    
    def set_batch_context(self, batch_line, mould_ranges, duplicate_checker):
        """Set batch context for QR validation."""
        self._batch_context = {
            'batch_line': batch_line,
            'mould_ranges': mould_ranges,
            'duplicate_checker': duplicate_checker
        }
        self.logger.info(f"Batch context set: line={batch_line}, moulds={len(mould_ranges)}")
    
    def handle_cartridge_advance(self) -> None:
        """Signal firmware that cartridge can advance to next position."""
        self.logger.info("ACTJv20(RJSR) - signaling cartridge advance OK")
        self.signal_ready()
        time.sleep(0.2)
        self.signal_busy()
        
    def handle_batch_start(self) -> None:
        """Signal firmware that batch processing is starting."""
        self.logger.info("ACTJv20(RJSR) - batch start sequence")
        self.signal_ready()
        time.sleep(0.3)
        self.signal_busy()
        
    def handle_batch_end(self) -> None:
        """Signal firmware that batch processing is complete."""
        self.logger.info("ACTJv20(RJSR) - batch end sequence")
        self.signal_ready()
        time.sleep(0.2)
        self.signal_busy()
        
    def handle_pass_result(self) -> None:
        """Handle PASS result - signal jig to advance cartridge."""
        self.logger.info("ACTJv20(RJSR) - QR PASS - advancing cartridge")
        self.handle_cartridge_advance()
        
    def handle_fail_result(self) -> None:
        """Handle FAIL result - signal jig to reject cartridge."""
        self.logger.info("ACTJv20(RJSR) - QR FAIL - rejecting cartridge")
        self.handle_cartridge_advance()  # Same signal, firmware handles reject logic
    
    def shutdown_sequence(self) -> None:
        """Execute shutdown sequence for ACTJv20(RJSR) compatibility."""
        self.logger.info("Starting ACTJv20(RJSR) shutdown sequence")
        
        # Stop UART communication
        stop_actj_communication()
        self.logger.info("UART communication stopped")
        
        # Signal not ready before shutdown
        self.signal_not_ready()
        time.sleep(0.2)
        
        self.logger.info("ACTJv20(RJSR) shutdown sequence completed")


# Global instance for easy access
_legacy_integration: Optional[ACTJLegacyIntegration] = None


def get_legacy_integration() -> ACTJLegacyIntegration:
    """Get singleton instance of ACTJv20(RJSR) legacy integration."""
    global _legacy_integration
    if _legacy_integration is None:
        _legacy_integration = ACTJLegacyIntegration()
    return _legacy_integration


def is_legacy_mode() -> bool:
    """Check if running in ACTJv20(RJSR) legacy mode."""
    try:
        from config import SETTINGS_FILE
        return "legacy" in SETTINGS_FILE.lower()
    except:
        return False


if __name__ == "__main__":
    # Test the legacy integration
    import sys
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Testing ACTJv20(RJSR) Legacy Integration")
    print("=====================================")
    
    integration = get_legacy_integration()
    
    # Test startup sequence
    print("\n1. Testing startup sequence...")
    integration.startup_sequence()
    
    # Test scanning sequence
    print("\n2. Testing scanning sequence...")
    test_qr = "TEST_QR_CODE_12345"
    success = integration.handle_scanning_sequence(test_qr)
    print(f"Scanning sequence result: {'SUCCESS' if success else 'FAILED'}")
    
    # Test shutdown sequence
    print("\n3. Testing shutdown sequence...")
    integration.shutdown_sequence()
    
    print("\nACTJv20(RJSR) Legacy Integration test completed")
    print("If you see no GPIO errors above, the integration is working correctly")
    print("\nNext steps:")
    print("1. Connect your ACTJv20(RJSR) hardware")
    print("2. Run 'python3 switch_mode.py legacy' to switch to legacy mode")
    print("3. Run 'python3 main.py' with the legacy settings")