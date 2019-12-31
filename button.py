import pycom
import time
from machine import Pin

pycom.heartbeat(False)

button = Pin('P10', mode=Pin.IN, pull=Pin.PULL_UP)

print('setup ready')
while True:
    while button():
        print('button not pressed')
        time.sleep(0.1)
    print('button pressed')
    pycom.rgbled(0x007f00) # green
    time.sleep(5)
    pycom.rgbled(0x7f7f00) # yellow
    time.sleep(1.5)
    pycom.rgbled(0x7f0000) # red
    time.sleep(4)
    pycom.rgbled(0x000000) # green
