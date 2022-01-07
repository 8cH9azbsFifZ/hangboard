#!/usr/bin/env python
import time
from datetime import datetime

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.virtual import viewport, sevensegment


def main():
    # create seven segment device
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=1)
    seg = sevensegment(device)

    for _ in range(2):
        seg.text = "HANG"
        time.sleep(0.6)
        seg.text = "7   3 "
        time.sleep(0.6)

    seg.text = "3 ..."
    for intensity in range(15,0,-1):
         seg.device.contrast(intensity * 16)
         time.sleep(1/16)
    seg.text = "2 .."
    for intensity in range(15,0,-1):
         seg.device.contrast(intensity * 16)
         time.sleep(1/16)
    seg.text = "1 ."
    for intensity in range(15,0,-1):
         seg.device.contrast(intensity * 16)
         time.sleep(1/16)
    seg.text = "0 "
    for intensity in range(15,0,-1):
         seg.device.contrast(intensity * 16)
         time.sleep(1/16)


    device.contrast(0x7F)
    seg.text = "10  20 "
    time.sleep(5)

if __name__ == '__main__':
    main()
