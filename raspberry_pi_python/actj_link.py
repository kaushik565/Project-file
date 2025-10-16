import time
import logging
from typing import Optional, Callable

try:
    import serial
    from serial import SerialException
except Exception:
    serial = None
    SerialException = Exception

try:
    import RPi.GPIO as GPIO
except Exception:
    GPIO = None

CMD_RETRY = 0x14  # 20
CMD_FINAL = 0x13  # 19

RES_ACCEPT = b"A"
RES_REJECT = b"R"
RES_DUPL   = b"D"
RES_SKIP   = b"S"

class ACTJLink:
    def __init__(self, port: str = "/dev/ttyS0", baudrate: int = 115200, busy_pin: int = 12, poll_ms: int = 20):
        self.port = port
        self.baudrate = baudrate
        self.busy_pin = busy_pin
        self.poll_ms = poll_ms
        self.ser: Optional[serial.Serial] = None if serial else None
        self.log = logging.getLogger("actj.link")

    def open(self) -> bool:
        if serial is None:
            self.log.error("pyserial not available")
            return False
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0)
        except SerialException as exc:
            self.log.error("serial open failed: %s", exc)
            return False
        if GPIO:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.busy_pin, GPIO.OUT, initial=GPIO.HIGH)  # idle high
        return True

    def close(self) -> None:
        try:
            if self.ser:
                self.ser.close()
        finally:
            self.ser = None
            if GPIO:
                GPIO.cleanup(self.busy_pin)

    def _set_busy(self, busy: bool):
        if not GPIO:
            return
        GPIO.output(self.busy_pin, GPIO.LOW if not busy else GPIO.HIGH)

    def loop(self, on_scan: Callable[[bool], bytes]):
        """
        Poll for PIC commands and respond.
        on_scan(final_attempt: bool) -> one of RES_ACCEPT/RES_REJECT/RES_DUPL/RES_SKIP
        """
        if not self.ser:
            raise RuntimeError("link not open")
        while True:
            b = self.ser.read(1)
            if not b:
                time.sleep(self.poll_ms / 1000.0)
                continue
            cmd = b[0]
            if cmd in (CMD_RETRY, CMD_FINAL):
                final_attempt = (cmd == CMD_FINAL)
                # Ack by dropping busy
                self._set_busy(False)
                time.sleep(0.02)
                try:
                    res = on_scan(final_attempt)
                    if res not in (RES_ACCEPT, RES_REJECT, RES_DUPL, RES_SKIP):
                        res = RES_SKIP
                    self.ser.write(res)
                    self.ser.flush()
                finally:
                    self._set_busy(True)
            else:
                self.log.debug("ignore byte 0x%02X", cmd)
