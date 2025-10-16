import logging
from actj_link import ACTJLink, RES_ACCEPT, RES_REJECT, RES_DUPL, RES_SKIP

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

# Simple demo policy: alternate PASS/REJECT
_state = {"i": 0}

def on_scan(final: bool):
    i = _state["i"]
    _state["i"] = i + 1
    if i % 3 == 0:
        return RES_ACCEPT
    if i % 3 == 1:
        return RES_REJECT
    return RES_DUPL

if __name__ == "__main__":
    link = ACTJLink(port="/dev/ttyS0", baudrate=115200, busy_pin=12)
    if not link.open():
        raise SystemExit(1)
    try:
        link.loop(on_scan)
    finally:
        link.close()
